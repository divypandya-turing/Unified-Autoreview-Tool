"""This script contains class that handles validations for the CODE block."""

import re
from typing import Optional

from parsing.block_parser import BaseBlock
from review_services.sft_validator.block_validations import BaseBlockValidators


class CODEValidator(BaseBlockValidators):
    """
    This class handles validations for the CODE block.
    """

    def __init__(self, block: BaseBlock, turn_idx: int, datasets: dict[str, str], skip_rows_count: dict[str, int]):
        super().__init__(block, turn_idx)
        self.datasets = datasets
        self.skip_rows_count = skip_rows_count

    def has_code_reading_from_invalid_sources(self) -> Optional[str]:
        """
        Check if any code block is reading from disallowed sources (e.g., '/cns/', 'url', etc.).
        """
        if self._block.matched_tag == "CODE:" and self._block.content:
            code = "\n".join(self._block.content)
            if any(
                invalid_source in code.lower()
                for invalid_source in [
                    ".read_csv('/cns/",
                    ".read_excel(",
                    " url",
                    "url.",
                    "url=",
                ]
            ):
                return self._msg + [f"[{self._block.matched_tag}]: CODE_READING_INVALID_SOURCE"]
        return None

    def has_matplotlib_plot(self) -> Optional[str]:
        """
        Check if the code block contains matplotlib plot code.
        """
        if self._block.matched_tag == "CODE:" and self._block.content:
            code = "\n".join(self._block.content)
            if any(matplotlib_keyword in code for matplotlib_keyword in ["matplotlib.pyplot", "plt.show"]):
                return self._msg + [f"[{self._block.matched_tag}]: MATPLOTLIB_PLOT_FOUND"]
        return None

    def has_invalid_file_name_in_code(self):
        """
        Check if any code line contains an invalid file name.
        """
        if self._block.content:
            # Regular expression to find filenames
            if self._block.content:
                csv_files = re.findall(r'pd\.read_csv\([\'"]([^\'\"]*\.[^\'\"]*)[\'"]\)', self._block.content[0])
                invalid_files = ", ".join([file for file in csv_files if file not in self.datasets])

                if invalid_files:
                    return self._msg + [f"[{self._block.matched_tag}]: CODE_INVALID_FILE_NAME '{invalid_files}'"]
            return None

    def has_altair_display(self) -> Optional[str]:
        """
        Check if Altair Chart code uses .display() instead of .save().
        """
        if self._block.content:
            code = "\n".join(self._block.content)
            # Check if code contains Altair Chart creation
            if "alt.Chart" in code or "altair.Chart" in code:
                if ".display" in code:
                    return self._msg + [f"[{self._block.matched_tag}]: USE_OF_ALTAIR_DISPLAY_DETECTED"]
        return None

    def has_altair_save(self) -> Optional[str]:
        """
        Validates that any alt.Chart usage includes .save() method.
        """
        if self._block.content:
            code = "\n".join(self._block.content)
            # Check if code contains Altair Chart creation
            if "alt.Chart" in code or "altair.Chart" in code:
                if ".save" not in code:
                    return self._msg + [f"[{self._block.matched_tag}]: ALTAIR_PLOT_MISSING_SAVE_METHOD"]
        return None

    def has_incorrect_skip_rows(self) -> Optional[str]:
        """
        Check if the skiprows parameter in read_csv matches the expected skip_rows_count for each file.
        """
        if not self._block.content or not self.skip_rows_count:
            return None

        code = "\n".join(self._block.content)

        # Find all read_csv calls with their file names
        file_matches = re.findall(r'pd\.read_csv\([\'"]([^\'"]*\.csv)[\'"]', code)

        for file_name in file_matches:
            if file_name in self.skip_rows_count:
                expected_skip_rows = self.skip_rows_count[file_name]

                # Look for skiprows parameter for this specific file
                file_code_pattern = rf'pd\.read_csv\([\'"]({file_name})[\'"][^)]*\)'
                file_code = re.search(file_code_pattern, code)
                if file_code:
                    skip_rows_match = re.search(r"skiprows\s*=\s*(\d+)", file_code.group(0))

                    # If skiprows parameter is missing
                    if not skip_rows_match:
                        return self._msg + [
                            f"[{self._block.matched_tag}]: MISSING_SKIPROWS_PARAMETER for {file_name} (should be {expected_skip_rows})"
                        ]

                    # If skiprows value doesn't match expected count
                    skip_rows = int(skip_rows_match.group(1))

                    if skip_rows != expected_skip_rows:
                        return self._msg + [
                            f"[{self._block.matched_tag}]: INCORRECT_SKIPROWS_VALUE for {file_name} (found {skip_rows}, should be {expected_skip_rows})"
                        ]

        return None

    def validate(self) -> list[list]:
        """
        Run all code-specific validations.

        Return
        ------
        List[list]
            A list of detected errors.
        """
        checks = [
            self.has_typo_in_tag,
            self.validate_content_exists,
            self.has_code_reading_from_invalid_sources,
            self.has_invalid_file_name_in_code,
            self.has_matplotlib_plot,
            # self.has_smart_quotes,
            self.has_altair_display,
            self.has_altair_save,
            self.has_incorrect_skip_rows,
        ]

        failed_checks = []
        for check in checks:
            check_id = check()
            if check_id:
                failed_checks.append(check_id)

        return failed_checks
