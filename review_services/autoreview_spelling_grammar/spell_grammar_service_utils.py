"""This file contains utility functions for the AutoReview Spelling and Grammar Service."""

import os

import requests
import yaml

from review_services.model_configs import AutoReview
from utils import logger


def query_endpoint(
    request: dict,
    iceFlowState: dict = {},
    stream: bool = False,
    verbose: bool = False,
    runFullIceFlowOnPrefilledState: bool = False,
) -> dict:
    """Query the AutoReview endpoint with the given request.

    Parameters
    ----------
    request : dict
        Request to send to the AutoReview endpoint.
    iceFlowState : dict, optional
        ICE Flow state to be used for the request, by default {}.
    stream : bool, optional
        Flag to enable streaming, by default False.
    verbose : bool, optional
        Flag to enable verbose output, by default False.
    runFullIceFlowOnPrefilledState : bool, optional
        Flag to run full ICE flow on prefilled state, by default False.

    Returns
    -------
    dict
        Response from the AutoReview endpoint.
    """
    # Send POST request
    model = request.get("model")
    try:

        method = "streamGenerateContent" if stream else "generateContent"

        request["bardConfig"] = {}

        response = requests.post(
            f"{AutoReview.URL}/v1beta/{model}:{method}?key={AutoReview.API_KEY}",
            json=request,
            headers={
                "Content-Type": "application/json",
            },
            timeout=1000,
        )
        response.raise_for_status()
        logger.info("Status Code: %s", response.status_code)
        return response.json()

    except requests.exceptions.HTTPError as e:
        logger.error("Request failed: %s", e)
        logger.error(e.request.url)
        logger.error(e)
        logger.error(e.response.text)
        raise e


def get_response_candidate_text(response: dict) -> str:
    """Get the response candidate text from the AutoReview response.

    Parameters
    ----------
    response : dict
        Response from the AutoReview endpoint.

    Returns
    -------
    str
        Response candidate text.
    """
    return response["candidates"][0]["content"]["parts"][0]["text"]


def process_autoreview_request(text: str) -> str:
    """Process the AutoReview request for the given text.

    Parameters
    ----------
    text : str
        Text to be processed.

    Returns
    -------
    str
        Processed text.
    """
    with open(os.path.join("review_services", "prompts_instructions.yaml")) as f:
        prompt_instructions = yaml.safe_load(f)
        prompt = prompt_instructions["autoreview_spelling_grammar"][1]["prompt"]
        system_instruction = prompt_instructions["autoreview_spelling_grammar"][0]["system_instruction"]

    autoreview_req = {
        "model": AutoReview.AUTORATER_MODEL_ALIAS,
        "generationConfig": {"candidateCount": 1},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": f"{prompt}\nText: {text}"},
                ],
            },
        ],
        "bardConfig": {
            "overwriteSystemInstruction": system_instruction,
        },
    }

    autoreview_resp = query_endpoint(autoreview_req)
    autoreview_resp_text = get_response_candidate_text(autoreview_resp)
    return autoreview_resp_text
