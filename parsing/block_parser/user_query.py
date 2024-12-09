"""This script contains USER_QUERY parsing class."""

from parsing.block_parser import BaseBlock


class UserQuery(BaseBlock):
    """
    A class representing the USER_QUERY in the plan.

    Attributes
    ----------
    serial_number (int): The serial number of the block.

    original_tag (str): The original tag as found in the input (including typos if any).

    matched_tag (str): The closest valid tag matched with the list of event tags.

    content (str): The raw content associated with the block (excluding the tag name).

    """
