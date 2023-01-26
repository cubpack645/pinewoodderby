from dataclasses import dataclass
import datetime
import itertools
import logging

from django.conf import settings

from rich.table import Table
from rich.console import Console
from fpdf import FPDF

from derby.core.models import RaceChart

logger = logging.getLogger(__name__)

COLORS = {
    "slowest": "red",
    "semis": "blue",
    "final": "green",
}

COLORS_RGB = {
    "slowest": (255, 0, 0),
    "semis": (0, 0, 255),
    "final": (0, 255, 0),
}


@dataclass
class GridCell:
    text: str
    style: str = ""

    def as_rich_table_cell(self):
        if self.style:
            color = COLORS.get(self.style)
            return f"[{color}]{self.text}"
        else:
            return self.text

    def as_pdf_cells(self):
        lines = []
        newlines = self.text.count("\n")
        if newlines == 0:
            lines = ["", self.text, "", ""]
        elif newlines == 2:
            lines = [*self.text.splitlines(), ""]
        elif newlines == 3:
            lines = self.text.splitlines()
        else:
            raise ValueError(
                f"Got {newlines} in a GridCell text field ({self.text=!r}), whats up with that?"
            )
        return lines

    def rgb_color(self):
        return COLORS_RGB.get(self.style) or (0, 0, 0)


class PdfTemplate(FPDF):
    def __init__(self, title):
        self.title = title
        self.created_on = datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p")
        super().__init__(orientation="L", unit="mm", format="Letter")

    def footer(self):
        self.set_text_color(0, 0, 255)
        self.set_font("helvetica", "", 8)
        self.set_y(-15)
        self.set_x(10)
        self.cell(120, 15, "Created By: Dave")
        self.set_x(130)
        self.cell(60, 15, f"Page {self.page_no()}", align="C")
        self.set_x(190)
        self.cell(60, 15, self.created_on, align="R")

    def add_grid_header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(200)
        self.cell(10, 6, "Heat", border=1, align="C", fill=True)
        for lane in range(1, settings.LANES + 1):
            self.cell(22, 6, f"Lane {lane}", border=1, align="C", fill=True)
        # reset font size back to normal grid output
        self.set_font("Helvetica", "", 8)
        self.ln()


class Command:
    def __init__(self, args):
        self.args = args

    def run(self):
        entries = self.get_annotated_entries()
        grid = self.create_grid_cells(entries)
        getattr(self, f"{self.args.output}_output")(grid)

    def pdf_output(self, grid):
        pdf = PdfTemplate("Den Finals Schedule (Annotated)")

        pdf.add_page()

        # first page header stuff
        pdf.set_font("Helvetica", "B", 16)
        # Rendering logo:
        pdf.image(str(settings.RESOURCES_DIR / "derby.png"), 10, 5, 45, 30)
        # Printing title:
        pdf.set_text_color(255, 0, 0)
        pdf.set_xy(40, 5)
        pdf.cell(190, 10, "Pack 645 Pinewood Derby 2023", align="C")
        pdf.set_text_color(0, 255, 0)
        pdf.set_xy(40, 15)
        pdf.cell(190, 10, "January 23 2023", align="C")
        pdf.set_text_color(0, 0, 255)
        pdf.set_xy(40, 25)
        pdf.cell(190, 10, "Den Finals (Annotated)", align="C")

        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(10, 40)

        pdf.set_xy(10, 40)
        pdf.set_text_color(0, 0, 0)

        pdf.add_grid_header()

        for grid_idx, grid_row in enumerate(grid, 1):
            if grid_idx == 9:
                pdf.add_page()
                pdf.add_grid_header()
            values = list(itertools.chain(*[cell.as_pdf_cells() for cell in grid_row]))
            for row_idx in range(4):
                row_values = values[row_idx::4]
                border = "LR"
                if row_idx == 0:
                    border += "T"
                elif row_idx == 3:
                    border += "B"
                for i, value in enumerate(row_values):
                    width = 10 if i == 0 else 22
                    pdf.set_text_color(*grid_row[i].rgb_color())
                    pdf.cell(width, 4.4, value, border, align="C")
                pdf.ln()
        pdf.output("/tmp/sauron.pdf", "F")

    def create_grid_cells(self, entries):
        max_heat = max(entry.heat for entry in entries.values())

        grid = []
        for heat in range(1, max_heat + 1):
            row = []
            row.append(GridCell(str(heat)))
            for lane in range(1, settings.LANES + 1):
                entry = entries.get((heat, lane))
                if not entry:
                    raise ValueError(f"No race chart entry for {heat=} {lane=}")
                else:
                    if entry.racer:
                        text = f"{entry.racer.carnumber}\n{entry.racer.firstname}\n{entry.racer.lastname}"
                        style = ""
                        if hasattr(entry, "annotation_text"):
                            text += f"\n{entry.annotation_text}"
                            style = entry.annotation_class
                        row.append(GridCell(text, style))
                    else:
                        row.append(GridCell("Bye"))
            grid.append(row)
        return grid

    def console_output(self, grid):
        table = Table(title="Dens Schedule (Annotated)", show_lines=True)

        table.add_column("Heat", justify="center")
        for lane in range(1, settings.LANES + 1):
            table.add_column(f"Lane {lane}", justify="center")

        for row in grid:
            table.add_row(*[cell.as_rich_table_cell() for cell in row])
        console = Console()
        console.print(table)

    def get_annotated_entries(self):
        def entry_keyfn(entry):
            return (entry.heat, entry.lane)

        schedules = self.get_schedules()
        lookups = self.get_lookups_by_car_number(schedules)

        results = {}
        for entry in schedules["dens"]:
            results_key = entry_keyfn(entry)

            racer = entry.racer
            if racer:
                slowest = lookups["slowest"].get(entry.racer.carnumber)
                if slowest:
                    entry.annotation_class = "slowest"
                    entry.annotation_text = f"Slowest: L{slowest.lane}"

                final = lookups["final"].get(entry.racer.carnumber)
                if final:
                    entry.annotation_class = "final"
                    entry.annotation_text = "Final"

                semis = lookups["semis"].get(entry.racer.carnumber)
                if semis:
                    entry.annotation_class = "semis"
                    entry.annotation_text = f"Semis: H{semis.heat} L{semis.lane}"

            results[results_key] = entry
        return results

    def get_lookups_by_car_number(self, schedules):
        ret = {}
        for round_name, schedule in schedules.items():
            if round_name == "dens":
                continue
            lookup = {entry.racer.carnumber: entry for entry in schedule}
            ret[round_name] = lookup
        return ret

    def get_schedules(self):
        schedules = {}
        for round in ("dens", "slowest", "semis", "final"):
            schedules[round] = (
                RaceChart.objects.filter(
                    classid=settings.ROUND_CONFIG[round]["class_id"]
                )
                .select_related("racer")
                .order_by("heat", "lane")
            )
        return schedules
