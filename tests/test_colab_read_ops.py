import unittest
from unittest.mock import patch

from utils.colab_read_ops import get_colabs, get_sft_and_stepwise_info
from utils.const import FOLDERS_TO_IGNORE


class TestColabReadOps(unittest.TestCase):
    """Test cases for colab_read_ops.py"""

    def test_get_sft_and_stepwise_info(self):
        """Test the get_sft_and_stepwise_info function."""
        test_cases = [
            ("Folder With_File Stepwise", "file", True),
            ("Folder No_File", "no_file", False),
            ("Folder PDF Stepwise", "pdf", True),
            ("Folder Search", "search", False),
            ("Folder Browse Stepwise", "browse", True),
            ("Folder Reasoning", "reasoning", False),
            ("Folder Marketing Stepwise", "marketing", True),
            ("Just a Folder", "other", False),
            ("Stepwise Folder", "other", True),  # Stepwise can be standalone
        ]
        for folder_name, expected_sft_type, expected_is_stepwise in test_cases:
            sft_type, is_stepwise = get_sft_and_stepwise_info(folder_name)
            self.assertEqual(sft_type, expected_sft_type)
            self.assertEqual(is_stepwise, expected_is_stepwise)

    @patch("utils.colab_read_ops.DRIVE_SERVICE")
    def test_get_colabs(self, mock_drive_service):
        """Test the get_colabs function."""
        mock_drive_service.files.return_value.list.return_value.execute.side_effect = [
            {
                "files": [
                    {"id": "folder1", "name": "Subfolder1", "mimeType": "application/vnd.google-apps.folder"},
                    {"id": "file1", "name": "File1.ipynb", "mimeType": "application/vnd.google-apps.notebook"},
                ]
            },
            {
                "files": [
                    {"id": "file2", "name": "TODO File2.ipynb", "mimeType": "application/vnd.google-apps.notebook"},
                    {"id": "file3", "name": "File3.ipynb", "mimeType": "application/vnd.google-apps.notebook"},
                ]
            },
            {},
        ]

        expected_colabs = [
            {"id": "file1", "name": "File1.ipynb", "sft_type": "other", "is_stepwise": False},
            {"id": "file3", "name": "File3.ipynb", "sft_type": "other", "is_stepwise": False},
        ]
        colabs = sorted(get_colabs("root_folder", "Root Folder"), key=lambda x: x["id"])
        self.assertEqual(colabs, expected_colabs)

    @patch("utils.colab_read_ops.DRIVE_SERVICE")
    def test_get_colabs_ignores_folders(self, mock_drive_service):
        """Test the get_colabs function ignores folders in FOLDERS_TO_IGNORE."""
        mock_drive_service.files.return_value.list.return_value.execute.return_value = {
            "files": [
                {"id": "folder1", "name": FOLDERS_TO_IGNORE[0], "mimeType": "application/vnd.google-apps.folder"},
            ]
        }
        colabs = get_colabs("root_folder", "Root Folder")

        self.assertEqual(colabs, [])  # Expect empty list as the folder should be ignored

    @patch("utils.colab_read_ops.DRIVE_SERVICE")
    def test_get_colabs_inherits_sft_type(self, mock_drive_service):
        """Test the get_colabs function inherits SFT type from parent folder."""
        mock_drive_service.files.return_value.list.return_value.execute.side_effect = [
            {
                "files": [
                    {"id": "folder1", "name": "Subfolder With_File", "mimeType": "application/vnd.google-apps.folder"},
                ]
            },
            {
                "files": [
                    {"id": "file1", "name": "File1.ipynb", "mimeType": "application/vnd.google-apps.notebook"},
                ]
            },
            {},
        ]

        expected_colabs = [
            {"id": "file1", "name": "File1.ipynb", "sft_type": "file", "is_stepwise": False},
        ]
        colabs = get_colabs("root_folder", "Root Folder")
        self.assertEqual(colabs, expected_colabs)
