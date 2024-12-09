"""This file contain class that stores the colab information and parsed colab plan."""

from parsing import ColabPlanParser
from parsing.colab_to_plan import create_a_plan_from_drive_notebook
from utils import logger


class Colab:
    def __init__(self, file_info: dict[str, str]):
        self.file_info: dict[str, str] = file_info
        self.file_name: str = file_info["name"]
        file_id: str = file_info["id"]
        self.colab_url: str = f"https://colab.research.google.com/drive/{file_id}"
        self.colab_res: dict[str, str] = {"colab_name": file_info["name"], "colab_url": self.colab_url}

        colab_plan_str = create_a_plan_from_drive_notebook(file_id)

        try:
            # Initialize the parser
            self.parsed_colab = ColabPlanParser(colab_plan_str, file_info["sft_type"], file_info["is_stepwise"])
        except Exception as e:
            logger.error(f"Error while parsing the plan: {e}")
            self.parsed_colab = None
