"""This file contains the Constants and Classes for the SFT Validator Service."""

import pandas as pd

from utils import SHEETS_SERVICE


class OnlineSFTCodeErrors:
    """A class for managing code errors from an online spreadsheet.

    This class fetches data from a Google Sheets document and stores it
    in a DataFrame. It exposes only `res_dict`, a dictionary containing
    selected data from the DataFrame.

    Attributes:
        res_dict (dict): A dictionary with 'Shared Link' as keys and 'Number of Expected Code Errors' as values.
    """

    res_dict = {}  # Static attribute for the exposed dictionary

    @classmethod
    def initialize_res_df(cls):
        """Initializes the `res_df` DataFrame and `res_dict` dictionary if they haven't been initialized.

        Fetches data from a specified Google Sheets spreadsheet and stores it
        in the `res_df` class attribute. Then, filters the DataFrame to create
        the `res_dict` dictionary, exposing only selected columns.

        Spreadsheet details:
            - Spreadsheet ID: "1-zQEB5kgQ9ydCskdhvTPGW0YfZD0qb3bkkSKZNItP8Q"
            - Sheet name: "09/06"

        Raises:
            googleapiclient.errors.HttpError: If there's an error accessing the Google Sheets API.
        """
        res_df = None
        if res_df is None:
            spreadsheet_id, sheet_name = "1-zQEB5kgQ9ydCskdhvTPGW0YfZD0qb3bkkSKZNItP8Q", "09/06"
            vals = (
                SHEETS_SERVICE.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=sheet_name)
                .execute()
                .get("values", [])
            )
            if len(vals) > 0:
                res_df = pd.DataFrame(vals[1:], columns=vals[0])

                # Generate res_dict from the specified columns
                if "SFT File Name" in res_df.columns and "Number of Expected Code Errors" in res_df.columns:
                    cls.res_dict = res_df.set_index("SFT File Name")["Number of Expected Code Errors"].to_dict()

    def __init__(self):
        """Initializes an instance of OnlineSFTCodeErrors.

        Calls the `initialize_res_df` class method to ensure that the `res_df`
        DataFrame and `res_dict` dictionary are initialized and available for use by instances.
        """
        self.initialize_res_df()


class BaseSFTSequence:
    """This is a base class containing the initial and repeating sequences for all SFTs"""

    init_seq = [
        "USER_QUERY:",
    ]

    repeating_seq = []


class FileSFTSequence(BaseSFTSequence):
    """This class contains the initial sequence for SFTs with FILE"""

    init_seq = [
        "USER_QUERY:",
        "ICE_FILE_METADATA:",
        "THOUGHT:",
    ]


class PDFSFTSequence(BaseSFTSequence):
    """This class contains the initial sequence for SFTs with PDF"""

    init_seq = [
        "USER_QUERY:",
        "ICE_FILE_METADATA:",
    ]
