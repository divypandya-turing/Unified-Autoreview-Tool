"""This script contains class that handles validations for the THOUGHT block."""

import re

from parsing.block_parser import BaseBlock
from review_services.sft_validator.block_validations import BaseBlockValidators


class ThoughtValidators(BaseBlockValidators):
    """
    This class handles validations for the THOUGHT block.
    """

    def __init__(self, block: BaseBlock, turn_idx: int, datasets: dict[str, str]):
        """Initialise the ThoughtValidators instance.

        Parameters
        ----------
        block : BaseBlock
            thought block to be validated.
        turn_idx : int
            turn number
        datasets : Dict[str, str]
            dictionary of valid {file_name: file_path} uploaded by user.
        """
        super().__init__(block, turn_idx)
        self.datasets = datasets

    def has_thought_reading_from_invalid_sources(self):
        """
        Check if any thought block contains references to invalid data sources.
        """
        if self._block.content and self._block.sft_type not in ["search", "browse"]:
            thought_text = self._block.content[0]
            if any(
                invalid_source in thought_text.lower()
                for invalid_source in [
                    ".read_csv('/cns/",
                    ".read_excel(",
                    " url",
                    "url.",
                    "url=",
                ]
            ):
                return self._msg + [f"[{self._block.matched_tag}]: THOUGHT_INVALID_SOURCE"]
        return None

    def has_invalid_file_name_in_thought(self):
        """
        Check if any thought block contains an invalid file name.
        """
        if self._block.content and self._block.is_file_loading_thought:
            files: list[str] = re.findall(r'[\'"]([^\'\"]*?\.[A-Za-z]+)[\'"]', self._block.content[0])
            files = [file for file in files if not file.strip('"').startswith("https://")]
            invalid_files = ", ".join([file.strip('"') for file in files if file.strip('"') not in self.datasets])

            if invalid_files:
                return self._msg + [f"[{self._block.matched_tag}]: THOUGHT_INVALID_FILE_NAME '{invalid_files}'"]
        return None

    def validate(self) -> list[list]:
        """
        Run all Thought-specific validations.

        Returns
        ------
        List[str]
            A list of failed check IDs.
        """
        checks = [
            self.has_typo_in_tag,
            self.validate_content_exists,
            self.has_thought_reading_from_invalid_sources,
            self.has_invalid_file_name_in_thought,
            # self.has_smart_quotes,
        ]

        failed_checks = []
        for check in checks:
            check_id = check()
            if check_id:
                failed_checks.append(check_id)

        return failed_checks
