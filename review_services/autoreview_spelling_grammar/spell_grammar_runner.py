"""This file contains the function to run the AutoReview Spelling and Grammar Service."""

import re

from review_services.autoreview_spelling_grammar.spell_grammar_service_utils import process_autoreview_request
from review_services.colab import Colab
from utils import Status


def parse_result(response: str) -> dict[str, str]:
    """Parse the result from the AutoReview endpoint.

    Parameters
    ----------
    response : str
        Text to parse.

    Returns
    -------
    dict[str, str]
        Parsed result.
    """
    match = re.search(r"\bNo Issues\b", response)
    if match:
        return {"status": Status.PASSED, "errors": None}

    errors = []
    for error in response.split("\n\n"):
        try:
            turn, block, err_type, err_msg = error.split(",")
            turn_num, block_num = int(turn.strip().split(" ")[-1]), int(block.strip().split(" ")[-1])
            errors.append([turn_num, block_num, f"[{err_type}]: {err_msg}"])
        except ValueError:
            errors.append([None, None, error])

    return {"status": Status.FAILED, "errors": errors}


def spell_grammar_autoreview(colab: Colab) -> Colab:
    """Function to process a single Colab file.

    Parameters
    ----------
    colab : Colab
        Colab object containing the Colab name, URL, and parsed Colab.

    Returns
    -------
    Colab
        Colab object containing the Colab name, URL, and errors (if any).
    """
    if colab.parsed_colab is None:
        colab.colab_res["errors"] = None
        colab.colab_res["status"] = "colab parsing failed"
        return colab

    # Process the request
    text = ""
    for turn in colab.parsed_colab.get_turns():
        for block in turn.blocks:
            if block.matched_tag in ["THOUGHT:", "RESPONSE_TO_USER:"]:
                text += f"Turn {turn.idx}, Block {block.serial_number}, {block.matched_tag}: {block.content[0]}\n"

    response = process_autoreview_request(text)
    parsed_response = parse_result(response)
    colab.colab_res["errors"] = parsed_response.get("errors")
    colab.colab_res["status"] = parsed_response.get("status")

    return colab
