"""This file contains constants used in the project."""

FOLDERS_TO_IGNORE: list[str] = [
    "[Deprecated - Ignore - Old] Workspace_ICE",
    "[Deprecated - Ignore] Workspace",
    "[Deprecated - Ignore] Workspace & Long Docs Multi-tool",
    "i18n",
]

# List of possible tags provided
EVENTS_TAG_UNIQUE_COLAB = [
    "TURN:",
    "USER_QUERY:",
    "ICE_FILE_METADATA:",
    "DOC_RELEVANCE_RETRIEVAL:",
    "DOC_RELEVANCE_RETRIEVAL_OUT:",
    "REWRITTEN_QUERY:",
    "THOUGHT:",
    "CODE:",
    "CODE_OUTPUT:",
    "RESPONSE_TO_USER:",
    "TOOL_CODE:",
    "TOOL_OUTPUT:",
]

# List of valid sub-tags for ICE_FILE_METADATA
FILE_METADATA_SUB_TAGS = [
    "file_name:",
    "previous_turn_number:",
    "ice_file_source:",
    "file_type:",
    "FILE_PATH:",
    "file_path:",
]

OPTIONAL_FILE_METADATA_SUB_TAGS = [
    "estimated_rows_above_header:",
]


class Status:
    """Class to define status constants."""

    PASSED = "Passed"
    FAILED = "Failed"
