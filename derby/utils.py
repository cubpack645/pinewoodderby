import colorlog
import datetime


def parse_date(raw):
    if raw == "today":
        return datetime.date.today()
    elif raw == "tomorrow":
        return datetime.date.today() + datetime.timedelta(days=1)
    else:
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
            try:
                return datetime.datetime.strptime(raw, fmt).date()
            except ValueError:
                pass
    raise ValueError(f"Invalid date {raw!r} supplied")


def configure_logging(level):
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)s:%(name)s:%(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )
    logger = colorlog.getLogger()
    logger.addHandler(handler)
    logger.setLevel(level)
