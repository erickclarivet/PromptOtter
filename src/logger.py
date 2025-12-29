import logging
import sys
from os import getenv
from dotenv import load_dotenv
load_dotenv()
DAYS = getenv("DAYS", "7")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # to print DEBUG, INFO, WARNING, ERROR, CRITICAL
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
# create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)
# add it
logger.addHandler(console_handler)