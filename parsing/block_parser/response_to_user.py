"""This script contains RESPONSE_TO_USER parsing class."""

from parsing.block_parser import BaseBlock


class RTU(BaseBlock):
    """
    A class representing the RESPONSE_TO_USER in the plan.

    Attributes
    ----------
    serial_number (int): The serial number of the block.

    original_tag (str): The original tag as found in the input (including typos if any).

    matched_tag (str): The closest valid tag matched with the list of event tags.

    content (str): The raw content associated with the block (excluding the tag name).

    """

    def __parse_content_for_code_snippent(self):
        """This method parses the RESPONSE_TO_USER block.
        It splits the content into plain text and code snippet.
        """
        plain_text = code_snippet = ""
        for text in enumerate("\n".join(self.content).split("```")):
            if text[0] % 2 == 0:
                plain_text += text[1]
            else:
                code_snippet += text[1]
        self.content = [plain_text, code_snippet]

    def parse_block(self):
        self.__parse_content_for_code_snippent()
