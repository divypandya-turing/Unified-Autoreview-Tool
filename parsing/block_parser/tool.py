"""This script contains TOOL_CODE and TOOL_OUTPUT parsing classes."""

import re
from typing import Optional

from parsing.block_parser import BaseBlock


class ToolCode(BaseBlock):
    """
    A class representing the TOOL_CODE in the plan.

    Attributes
    ----------
    serial_number (int): The serial number of the block.

    original_tag (str): The original tag as found in the input (including typos if any).

    matched_tag (str): The closest valid tag matched with the list of event tags.

    content (str): The raw content associated with the block (excluding the tag name).

    """


class ToolOutput(BaseBlock):
    """
    A class representing the TOOL_OUTPUT in the plan.

    Attributes
    ----------
    sft_type (str): The type of SFT.

    serial_number (int): The serial number of the block.

    original_tag (str): The original tag as found in the input (including typos if any).

    matched_tag (str): The closest valid tag matched with the list of event tags.

    content (str): The raw content associated with the block (excluding the tag name).

    metadata (dict): A dictionary storing parsed metadata.
    """

    def __init__(self, sft_type, serial_number, original_tag, matched_tag, content):
        """
        Initializes the ToolOutput instance.

        Parameters
        ----------
        sft_type (str): The type of SFT.

        serial_number (int): The serial number of the block.

        original_tag (str): The original tag as found in the input (with typos).

        matched_tag (str): The closest valid tag from the provided event tags.

        content (str): The content associated with the block (excluding the tag name).
        """
        super().__init__(sft_type, serial_number, original_tag, matched_tag, content)

        # Instance attribute to hold parsed metadata
        self.metadata: Optional[dict] = {}

    def __parse_tool_output(self):
        """Parses the content for TOOL_OUTPUT section into a dictionary."""
        try:
            # Join non-empty strings with commas and strip whitespaces
            str_content = ", ".join([s.strip() for s in self.content if s.strip()])

            # Replace single quotes with double quotes and format dictionary structure
            str_content = (
                str_content.replace("'", '"').replace("{", ": {").replace(": {,", ": {")  # Format nested dictionaries
            )  # Fix misplaced delimiters

            # Remove space between colons and words
            str_content = re.sub(r"\s+(:)", r"\1", str_content)

            # Fix key-value pairs: add quotes around keys and ensure proper comma placement
            str_content = re.sub(r"(\w+):", r'"\1":', str_content)
            str_content = re.sub(r'(?<=\w)"\s+', '", ', str_content)

            # Replace specific keywords with quoted versions
            str_content = str_content.replace("FILE_SOURCE_TOOL_GENERATED", '"FILE_SOURCE_TOOL_GENERATED"').replace(
                "FILE_TYPE_TEXT", '"FILE_TYPE_TEXT"'
            )

            # Fix 'https' issue by removing any misplaced quotes
            str_content = str_content.replace('https":', "https:").replace('""', '"')

            # Evaluate the string as a Python dictionary
            self.metadata = eval(f"{{{str_content}}}")
            if isinstance(self.metadata, set):
                self.metadata = {}
        except Exception:
            self.metadata = {}

    def parse_block(self):
        self.__parse_tool_output()

    def __str__(self):
        """
        Returns a string representation of the block instance.

        Returns
        -------
        str: A formatted string displaying the block's serial number, tags, and content.
        """
        return (
            f"Serial Number: {self.serial_number}\n"
            f"Original Tag: {self.original_tag}\n"
            f"Matched Tag: {self.matched_tag}\n"
            f"Metadata:\n{self.metadata}\n"
        )
