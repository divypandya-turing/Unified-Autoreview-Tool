"""This file contains base block validator class."""

from abc import abstractmethod
from typing import Optional

from parsing.block_parser import BaseBlock


class BaseBlockValidators:
    """
    Base class for block-level validations.
    """

    def __init__(self, block: BaseBlock, turn_idx: int):
        """Initialise the BaseBlockValidators instance.

        Parameters
        ----------
        block : BaseBlock
            The block to be validated.
        turn_idx : int
            The index of the turn.
        """
        self._block: BaseBlock = block
        self._msg: list = [turn_idx, block.serial_number]

    def has_typo_in_tag(self) -> Optional[str]:
        """Check for typos in the block tag."""
        if self._block.matched_tag != self._block.original_tag:
            return self._msg + [f"[{self._block.original_tag}] TYPO_IN_TAG, SHOULD_BE '{self._block.matched_tag}'"]
        return None

    def validate_content_exists(self) -> Optional[list]:
        """Ensure that every block has content."""
        if not "".join(self._block.content):
            return self._msg + [f"[{self._block.matched_tag}]: MISSING_CONTENT"]
        return None

    def has_smart_quotes(self) -> Optional[list]:
        """Check for smart quotes in the block content."""
        smart_quotes = ["’", "’"]
        if self._block.content:
            content = (
                self._block.content[0] if isinstance(self._block.content[0], str) else "\n".join(self._block.content[0])
            )
            if any(quote in content for quote in smart_quotes):
                return self._msg + [f"[{self._block.matched_tag}]: SMART_QUOTES_FOUND"]
        return None

    @abstractmethod
    def validate(self):
        """Abstract method to be implemented by subclasses."""
