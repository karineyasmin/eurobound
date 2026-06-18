import logging
import sys
from colorama import init, Fore, Style

init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom CSV/ANSI formatter to add colors to terminal logs based on severity"""

    log_format = "%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) - %(message)s"

    FORMATS = {
        logging.DEBUG: Fore.LIGHTBLACK_EX + log_format,
        logging.INFO: Fore.BLUE + log_format,
        logging.WARNING: Fore.YELLOW + log_format,
        logging.ERROR: Fore.RED + log_format,
        logging.CRITICAL: Fore.RED + Style.BRIGHT + log_format,
    }

    def format(self, record):  # type: ignore
        log_fmt = self.FORMATS.get(record.levelno, self.log_format)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logger(name: str = "eurobound") -> logging.Logger:
    """Configures and returns a custom colored logger instance using colorama"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(ColoredFormatter())

        logger.addHandler(console_handler)
    return logger


logger = setup_logger()
