"""Logger For All Modules."""
import logging

logging.basicConfig(
    filename="app.log",
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)

# Suppress specific logging messages from googleapiclient.discovery_cache
logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
