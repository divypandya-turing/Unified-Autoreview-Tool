"""This script contains class that handles validations for the ICE_FILE_METADATA block."""

import re
from typing import Optional

from review_services.sft_validator.block_validations import BaseBlockValidators
from utils import FILE_METADATA_SUB_TAGS, OPTIONAL_FILE_METADATA_SUB_TAGS, initialize_drive_service, logger


class ICEFileMetadataValidators(BaseBlockValidators):
    """
    This class handles validations for the ICE_FILE_METADATA block.
    """

    def has_invalid_file_metadata_tag(self) -> Optional[str]:
        """Check for typos in the file_metadata tags."""
        metadata = self._block.metadata
        for file_tag in FILE_METADATA_SUB_TAGS + OPTIONAL_FILE_METADATA_SUB_TAGS:
            if file_tag == "file_path:":
                continue
            if file_tag in metadata:
                if metadata[file_tag]["original_tag"] != file_tag:
                    return self._msg + [
                        f"[{self._block.matched_tag}] "
                        f"'{metadata[file_tag]['original_tag']}' "
                        f"TYPO_IN_TAG, SHOULD_BE: '{file_tag}'"
                    ]
            elif file_tag in FILE_METADATA_SUB_TAGS:
                return self._msg + [f"[{self._block.matched_tag}] MISSING_TAG: '{file_tag}'"]
        return None

    def missing_input_file(self) -> Optional[str]:
        """Check if the ICE_FILE_METADATA block is missing input file information"""
        if "file_name:" not in self._block.metadata or not self._block.metadata["file_name:"]["value"]:
            return self._msg + [f"[{self._block.matched_tag}]: MISSING_INPUT_FILE"]
        return None

    def validate_file_name_format(self) -> Optional[str]:
        """Validate that the file_name in ICE_FILE_METADATA ends with .csv, .tsv, or .pdf."""
        if "file_name:" in self._block.metadata:
            file_name = self._block.metadata["file_name:"]["value"]
            if not file_name.endswith((".csv", ".tsv", ".pdf")):
                return self._msg + [f"[{self._block.matched_tag}]: INVALID_FILE_FORMAT"]
        return None

    def has_spreadsheet_url(self) -> Optional[str]:
        """Check if the FILE_PATH contains a spreadsheet URL."""
        if "FILE_PATH:" in self._block.metadata:
            file_path = self._block.metadata["FILE_PATH:"]["value"]
            if file_path.startswith("https://docs.google.com/spreadsheets/d/"):
                return self._msg + [f"[{self._block.matched_tag}]: SPREADSHEET_URL_FOUND in FILE_PATH"]
        return None

    def validate_filename_in_url_matches_file_name(self) -> Optional[str]:
        """Check if the filename in the Google Drive URL matches the expected file_name."""
        if "FILE_PATH:" in self._block.metadata and "file_name:" in self._block.metadata:
            file_path = self._block.metadata["FILE_PATH:"]["value"]
            file_name = self._block.metadata["file_name:"]["value"]

            # Extract file ID from FILE_PATH
            file_id = self.__get_file_id_from_link(file_path)
            if not file_id:
                return self._msg + [f"[{self._block.matched_tag}]: INVALID_FILE_PATH_FORMAT"]

            # Get actual filename from Google Drive and compare
            drive_file_name = self.__get_filename_from_drive(file_id)
            if drive_file_name:
                if drive_file_name != file_name:
                    return self._msg + [
                        f"[{self._block.matched_tag}]: FILENAME_MISMATCH - Expected: '{file_name}', "
                        f"Found: '{drive_file_name}' in the URL"
                    ]
            else:
                return self._msg + [f"[{self._block.matched_tag}]: FILE_URL_INVALID"]

        return None

    def __get_file_id_from_link(self, link: str) -> Optional[str]:
        """Extract the file ID from a Google Drive link."""
        match = re.search(r"/d/([a-zA-Z0-9_-]+)", link)
        return match.group(1) if match else None

    def __get_filename_from_drive(self, file_id: str) -> Optional[str]:
        """Retrieve the filename from Google Drive using the file ID."""

        try:
            drive_service = initialize_drive_service()
            file_metadata = drive_service.files().get(fileId=file_id, fields="name").execute()  # noqa
            return file_metadata.get("name")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None

    def validate(self) -> list[list]:
        """
        Run all block-specific validations.

        Returns
        ------
        List[str]
            A list of failed check IDs.
        """
        checks = [
            self.has_typo_in_tag,
            self.has_invalid_file_metadata_tag,
            self.missing_input_file,
            self.validate_file_name_format,
            self.has_spreadsheet_url,
            self.validate_content_exists,
            self.validate_filename_in_url_matches_file_name,
        ]

        failed_checks = []
        for check in checks:
            check_id = check()
            if check_id:
                failed_checks.append(check_id)

        return failed_checks
