"""This file contains Model Configurations for the AutoReview based services."""

import os

from dotenv import load_dotenv

load_dotenv()


class AutoReview:
    """This class contains configurations for AutoReview based services."""

    API_KEY = os.getenv("API_KEY")
    URL = "https://preprod-generativelanguage.googleapis.com"
    ICE_MODEL_ALIAS = "models/chat-bard-ice-eac-merge-sota-sft-model"
    AUTORATER_MODEL_ALIAS = "models/chat-bard-ice-autorater"
