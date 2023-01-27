from dataclasses import dataclass
import datetime
from fpdf import FPDF
import itertools
import logging

from django.conf import settings

from derby.core.models import RaceChart

logger = logging.getLogger(__name__)

COLORS_RGB = {
    "slowest": (255, 0, 0),
    "semis": (0, 0, 255),
    "final": (0, 255, 0),
}


class DenFinalsReport:
    def run(self, destination=settings.REPORTS_DIR / "den_finals_custom.pdf"):
        entries = self.get_annotated_entries()
        grid = self.create_grid_cells(entries)
        DenFinalsPdf().create(grid, destination)

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
                        text = f"{entry.racer.carnumber}\n{entry.racer.firstname} {entry.racer.lastname}"
                        style = ""
                        if hasattr(entry, "annotation_text"):
                            text += f"\n{entry.annotation_text}"
                            style = entry.annotation_class
                        row.append(GridCell(text, style))
                    else:
                        row.append(GridCell("Bye"))
            grid.append(row)
        return grid

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


class DenFinalsPdf:
    def __init__(self):
        self.font_name = "Helvetica"
        self.font_size_h1 = 16
        self.font_size_emphasis = 9
        self.font_size_normal = 8
        self.font_size_footer = 8
        self.created_on = datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p")

    def create(self, grid, destination):
        pdf = FPDF(orientation="L", unit="mm", format="Letter")
        pdf.set_auto_page_break(False)

        pdf.add_page()
        self.add_first_page_header(pdf)
        self.add_footer(pdf)

        pdf.set_xy(10, 40)
        self.add_grid_header(pdf)

        for grid_idx, grid_row in enumerate(grid, 1):
            if grid_idx == 12:
                pdf.add_page()
                x, y = pdf.get_x(), pdf.get_y()
                self.add_footer(pdf)
                pdf.set_xy(x, y)
                self.add_grid_header(pdf)
            values = list(itertools.chain(*[cell.as_lines() for cell in grid_row]))
            for row_idx in range(3):
                if row_idx == 0:
                    pdf.set_font(self.font_name, "B", self.font_size_emphasis)
                elif row_idx == 1:
                    pdf.set_font(self.font_name, "", self.font_size_normal)
                else:
                    pdf.set_font(self.font_name, "B", self.font_size_emphasis)
                row_values = values[row_idx::3]
                border = "LR"
                if row_idx == 0:
                    border += "T"
                elif row_idx == 2:
                    border += "B"
                for i, value in enumerate(row_values):
                    width = 10 if i == 0 else 30
                    pdf.set_text_color(*grid_row[i].rgb_color())
                    pdf.cell(width, 4.4, value, border, align="C")
                pdf.ln()
        pdf.output(destination, "F")

    def add_first_page_header(self, pdf):
        # first page header stuff
        pdf.set_font(self.font_name, "B", self.font_size_h1)
        # Rendering logo:
        pdf.image(str(settings.RESOURCES_DIR / "derby.png"), 10, 5, 45, 30)
        pdf.set_text_color(255, 0, 0)
        pdf.set_xy(40, 5)
        pdf.cell(190, 10, "Pack 645 Pinewood Derby 2023", align="C")
        pdf.set_text_color(0, 255, 0)
        pdf.set_xy(40, 15)
        pdf.cell(190, 10, "January 23 2023", align="C")
        pdf.set_text_color(0, 0, 255)
        pdf.set_xy(40, 25)
        pdf.cell(190, 10, "Den Finals (Annotated)", align="C")

    def add_grid_header(self, pdf):
        pdf.set_font(self.font_name, "B", self.font_size_emphasis)
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(200)
        pdf.cell(10, 6, "Heat", border=1, align="C", fill=True)
        for lane in range(1, settings.LANES + 1):
            pdf.cell(30, 6, f"Lane {lane}", border=1, align="C", fill=True)
        pdf.ln()

    def add_footer(self, pdf):
        pdf.set_text_color(0, 0, 255)
        pdf.set_font(self.font_name, "", self.font_size_footer)
        pdf.set_y(-15)
        pdf.set_x(10)
        pdf.cell(120, 15, "Created By: Dave")
        pdf.set_x(130)
        pdf.cell(60, 15, f"Page {pdf.page_no()}", align="C")
        pdf.set_x(190)
        pdf.cell(60, 15, self.created_on, align="R")
        pdf.ln()


@dataclass
class GridCell:
    text: str
    style: str = ""

    def as_lines(self):
        lines = []
        newlines = self.text.count("\n")
        if newlines == 0:
            lines = ["", self.text, ""]
        elif newlines == 1:
            lines = [*self.text.splitlines(), ""]
        elif newlines == 2:
            lines = self.text.splitlines()
        else:
            raise ValueError(
                f"Got {newlines} in a GridCell text field ({self.text=!r}), whats up with that?"
            )
        return lines

    def rgb_color(self):
        return COLORS_RGB.get(self.style) or (0, 0, 0)
