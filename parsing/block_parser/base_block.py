"""This script contains base block parsing class."""


class BaseBlock:
    """
    A class representing a block in the plan.

    Attributes
    ----------
    sft_type (str): The type of SFT.

    serial_number (int): The serial number of the block.

    original_tag (str): The original tag as found in the input (including typos if any).

    matched_tag (str): The closest valid tag matched with the list of event tags.

    content (str): The raw content associated with the block (excluding the tag name).
    """

    def __init__(self, sft_type: str, serial_number: int, original_tag: str, matched_tag: str, content: str):
        """
        Initializes a block instance.

        Parameters
        ----------

        sft_type (str): The type of SFT.

        serial_number (int): The serial number of the block.

        original_tag (str): The original tag as found in the input (with typos).

        matched_tag (str): The closest valid tag from the provided event tags.

        content (str): The content associated with the block (excluding the tag name).
        """
        self.sft_type: str = sft_type
        self.serial_number: int = serial_number
        self.original_tag: str = original_tag
        self.matched_tag: str = matched_tag
        self.content: list[str] = content

    def parse_block(self):
        """This method parses the block content."""
        return self

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
            f"Content:\n{self.content}\n"
        )
