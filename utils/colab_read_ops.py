"""This contains functions to read colabs."""

from utils.const import FOLDERS_TO_IGNORE
from utils.drive_auth import initialize_drive_service
from utils.logger import logger


def get_sft_and_stepwise_info(name: str) -> tuple[str, bool]:
    """Function to discern SFT type of the folder and if it is step-wise

    Parameters
    ----------
    name : str
        Name of folder or file

    Returns
    -------
    tuple[str, bool]
        SFT type and if it is step-wise
    """
    sft_type = "other"

    if "With_File" in name:
        sft_type = "file"
    elif "No_File" in name:
        sft_type = "no_file"
    elif "PDF" in name:
        sft_type = "pdf"
    elif "Search" in name:
        sft_type = "search"
    elif "Browse" in name:
        sft_type = "browse"
    elif "Reasoning" in name:
        sft_type = "reasoning"
    elif "Marketing" in name:
        sft_type = "marketing"

    is_stepwise = "Stepwise" in name

    return sft_type, is_stepwise


def get_colabs(folder_id: str, descriptive_name: str, filter_key_words: list = ["TODO"]) -> list[dict[str, str]]:
    """Function to read the colabs from the folder and its subfolders,
    while discerning the SFT type from parent and stepwise from child.

    Parameters
    ----------
    folder_id : str
        folder_id of the folder to read the colabs from.
    descriptive_name : str
        folder name
    filter_key_words : list, optional
        Keywords to filter out files, by default ['TODO']

    Returns
    -------
    list[dict[str, str]]
        List of colabs with SFT type and stepwise info
    """
    all_colab_folder_items = []
    drive_service = initialize_drive_service()

    def traverse_folders(folder_id: str, folder_name: str, parent_sft_type: str):
        """Helper function to recursively traverse through subfolders,
        inheriting SFT type from parent and determining stepwise at child level."""

        # Skip the folder if it is in the FOLDERS_TO_IGNORE list
        if folder_name in FOLDERS_TO_IGNORE:
            logger.info(f"Skipping folder: {folder_name}")
            return

        # If parent_sft_type is still "other", update it based on current folder name
        sft_type = parent_sft_type if parent_sft_type != "other" else get_sft_and_stepwise_info(folder_name)[0]

        # List all items in the current folder
        query = f"'{folder_id}' in parents and trashed=false"
        page_token: str = None
        while True:
            results = (
                drive_service.files()
                .list(q=query, fields="nextPageToken, files(id, name, mimeType)", pageToken=page_token)
                .execute()
            )
            items = results.get("files", [])
            for item in items:
                if item["mimeType"] == "application/vnd.google-apps.folder":  # Check if the item is a folder
                    # Traverse the subfolder, passing the sft_type from the parent
                    traverse_folders(item["id"], item["name"], sft_type)
                else:
                    # Determine stepwise information based on current folder name
                    is_stepwise = get_sft_and_stepwise_info(folder_name)[1] or "Stepwise" in item["name"]
                    all_colab_folder_items.append(
                        {"id": item["id"], "name": item["name"], "sft_type": sft_type, "is_stepwise": is_stepwise}
                    )  # Collect files with SFT type and stepwise info

            page_token = results.get("nextPageToken", None)
            if not page_token:
                break

    # Start traversal from the root folder, initially setting sft_type to "other"
    # traverse_folders(folder_id, descriptive_name, "other")
    # Check if the provided ID is a file or a folder
    file_metadata = drive_service.files().get(fileId=folder_id, fields="id, name, mimeType").execute()
    if file_metadata["mimeType"] == "application/vnd.google-apps.folder":
        # Start traversal from the root folder, initially setting sft_type to "other"
        traverse_folders(folder_id, descriptive_name, "other")
    elif file_metadata["mimeType"] in ["application/vnd.google.colab", "application/vnd.google.colaboratory"]:
        # Directly add the file to the list if it's a colab notebook
        sft_type, is_stepwise = get_sft_and_stepwise_info(file_metadata["name"])
        all_colab_folder_items.append(
            {"id": file_metadata["id"], "name": file_metadata["name"], "sft_type": sft_type, "is_stepwise": is_stepwise}
        )

    # Filter the items based on the filter keywords
    selected_colab_folder_items = list(
        filter(
            lambda x: x and all(filter_key_word not in x["name"] for filter_key_word in filter_key_words),
            all_colab_folder_items,
        )
    )

    logger.info(
        f"Selected {len(selected_colab_folder_items)} colabs from"
        f" {descriptive_name} folder: https://drive.google.com/drive/folders/{folder_id}"
    )

    return selected_colab_folder_items
