"""This script contains CODE and CODE_OUTPUT parsing classes."""

import json

from parsing.block_parser import BaseBlock


class Code(BaseBlock):
    """
    A class representing the CODE in the plan.

    Attributes
    ----------
    serial_number (int): The serial number of the block.

    original_tag (str): The original tag as found in the input (including typos if any).

    matched_tag (str): The closest valid tag matched with the list of event tags.

    content (str): The raw content associated with the block (excluding the tag name).

    """


class CodeOutput(BaseBlock):
    """
    A class representing the CODE_OUTPUT in the plan.

    Attributes
    ----------
    serial_number (int): The serial number of the block.

    original_tag (str): The original tag as found in the input (including typos if any).

    matched_tag (str): The closest valid tag matched with the list of event tags.

    content (str): The raw content associated with the block (excluding the tag name).

    """

    def __has_code_error(self):
        """This method checks if the CODE_OUTPUT contains code error."""
        self.has_code_error = False

        for output in json.loads(self.content[0]):
            if output["output_type"] == "error":
                self.has_code_error = True
                break

    def parse_block(self):
        self.__has_code_error()
