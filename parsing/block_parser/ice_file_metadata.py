"""This file contains Section class that contains info for a tag in
EVENTS_TAG_UNIQUE_COLAB."""

from typing import Optional

from parsing.block_parser import BaseBlock
from parsing.plan_parser_utils import get_closest_match
from utils import FILE_METADATA_SUB_TAGS, OPTIONAL_FILE_METADATA_SUB_TAGS


class ICEFileMetadata(BaseBlock):
    """
    This class handles the ICE_FILE_METADATA block.

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
        Initializes the ICEFileMetadata instance.

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

    def __parse_file_metadata(self):
        """
        Parses the metadata in the ICE_FILE_METADATA.
        """
        for line in self.content:
            if ":" in line:
                key, value = line.split(":", 1)
                corrected_key = get_closest_match(
                    key.lower().strip(), FILE_METADATA_SUB_TAGS + OPTIONAL_FILE_METADATA_SUB_TAGS
                )

                if corrected_key in ["file_path:", "FILE_PATH:"]:
                    corrected_key = "FILE_PATH:"
                self.metadata[corrected_key] = {
                    "original_tag": key + ":",
                    "value": value.strip().strip('"').strip("'"),
                }

    def parse_block(self):
        self.__parse_file_metadata()

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
