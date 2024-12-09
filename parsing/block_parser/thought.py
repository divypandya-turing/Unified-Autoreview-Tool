"""This script contains THOUGHT parsing class."""

from parsing.block_parser import BaseBlock


class Thought(BaseBlock):
    """
    A class representing the THOUGHT in the plan.

    Attributes
    ----------
    sft_type (str): The type of SFT.

    serial_number (int): The serial number of the block.

    original_tag (str): The original tag as found in the input (including typos if any).

    matched_tag (str): The closest valid tag matched with the list of event tags.

    content (str): The raw content associated with the block (excluding the tag name).

    """

    def __parse_content_for_code_snippent(self):
        """This method parses the THOUGHT block.
        It splits the content into plain text and code snippet.
        """
        plain_text = code_snippet = ""
        for text in enumerate("\n".join(self.content).split("```")):
            if text[0] % 2 == 0:
                plain_text += text[1]
            else:
                code_snippet += text[1]
        self.content = [plain_text, code_snippet]

    def __is_file_loading_thought(self):
        self.is_file_loading_thought = "load" in self.content[0].lower()

    def parse_block(self):
        self.__parse_content_for_code_snippent()
        self.__is_file_loading_thought()
