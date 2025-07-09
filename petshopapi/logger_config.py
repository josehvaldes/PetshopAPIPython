import logging
from petshopapi.config import settings

logging.basicConfig(
    #level=logging.INFO,
    level = settings["settings"]["log_level"].upper(),
    format="     ←[%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)
