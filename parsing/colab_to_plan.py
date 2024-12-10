"""This file contains function to create plan from drive colab notebooks."""


import json

import nbformat

from utils import initialize_drive_service, logger


def create_a_plan_from_colab_notebook(nb: nbformat.NotebookNode) -> list[tuple[str, str]]:
    """
    Creates a plan string from a Colab notebook by extracting markdown and code cells.

    Parameters
    ----------
    nb : nbformat.NotebookNode
        The notebook object in nbformat that contains the cells to be processed.

    Returns
    -------
    list[tuple[str, str]]]
        A formatted string with content from markdown cells and labeled code cells.
        Code cells are prefixed with "CODE:\n".
    """
    plan_lines = []

    # Iterate through each cell in the notebook
    for cell in nb.cells:
        # Check if the cell is of type markdown and contains content
        if cell.cell_type == "markdown":
            # Append the tuple ('markdown', content)
            plan_lines.append(("markdown", cell.source))

        # Check if the cell is of type code and contains content
        elif cell.cell_type == "code":
            # Append the tuple ('code', content)
            plan_lines.append(("code", cell.source))

            # Check if there are outputs associated with the code cell
            if cell.outputs and len(cell.outputs) > 0:
                cell_out = json.dumps(cell.outputs)

                # Append the tuple ('code_output', output content)
                plan_lines.append(("code_output", cell_out))

    # Return the list of tuples (cell_type, content)
    return plan_lines


def create_a_plan_from_drive_notebook(file_id: str):
    """
    Fetches a Jupyter notebook from Google Drive, processes it, and returns a formatted plan.

    Parameters
    ----------
    file_id : str
        The unique identifier of the file in Google Drive.

    Returns
    -------
    str or None
        A formatted string containing the notebook content if it's successfully processed.
        Returns None if the file is a folder or if any error occurs during processing.

    Notes
    -----
    - This function assumes access to the Google Drive API through `drive_service`.
    - Only files with a MIME type other than 'application/vnd.google-apps.folder' are processed.
    - The notebook is assumed to be in `nbformat` version 4.
    """
    try:
        # Fetch the file metadata to determine the MIME type and name
        drive_service = initialize_drive_service()
        file_metadata = drive_service.files().get(fileId=file_id, fields="name, mimeType").execute()  # noqa
        file_name, mime_type = file_metadata["name"], file_metadata["mimeType"]

        # Only process if it's not a folder
        if mime_type != "application/vnd.google-apps.folder":
            # Download the file content
            file_content = drive_service.files().get_media(fileId=file_id).execute()  # noqa

            # Try to load notebook into nbformat
            try:
                nb = nbformat.reads(file_content.decode("utf-8"), as_version=4)
                # Generate the plan string from the notebook content
                return create_a_plan_from_colab_notebook(nb)
            except Exception as error:
                logger.exception(f"Failed to load notebook: {file_name} ({file_id}) - {str(error)}")
                return None
        else:
            logger.exception(f"File {file_name} is a folder.")
            return None

    except Exception as error:
        logger.exception(f"An error occurred while retrieving the file: {str(error)}")
        return None
