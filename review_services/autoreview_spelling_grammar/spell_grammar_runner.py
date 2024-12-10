"""This file contains the function to run the AutoReview Spelling and Grammar Service."""

import re
import traceback

from review_services.autoreview_spelling_grammar.spell_grammar_service_utils import process_autoreview_request
from review_services.colab import Colab
from utils import Status, logger


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
            parts = error.split(",")
            turn, block, block_type, err_type = parts[:4]
            err_msg = ",".join(parts[4:])
            turn_num, block_num = int(turn.strip().split(" ")[-1]), int(block.strip().split(" ")[-1])
            errors.append([turn_num, block_num, f"{block_type.strip()} -> [{err_type.strip()}] -> {err_msg.strip()}"])
        except ValueError:
            err_traceback = traceback.format_exc()
            logger.error(f"ValueError while parsing: {error}")
            logger.error(err_traceback)
            errors.append([None, None, error])

    return {"status": Status.FAILED, "errors": errors}


def spell_grammar_autoreview(file_info: dict[str, str]) -> Colab:
    """Function to process a single Colab file.

    Parameters
    ----------
    file_info : dict[str, str]
        Dictionary containing the file information.

    Returns
    -------
    Colab
        Colab object containing the Colab name, URL, and errors (if any).
    """
    colab: Colab = Colab(file_info)
    if colab.parsed_colab is None:
        colab.colab_res["errors"] = None
        colab.colab_res["status"] = "colab parsing failed"
        return colab

    # Process the request
    text = ""
    for turn in colab.parsed_colab.get_turns():
        for block in turn.blocks:
            if block.matched_tag in ["THOUGHT:", "RESPONSE_TO_USER:"]:
                text += f"Turn {turn.idx}, Block {block.serial_number}, [{block.matched_tag}] {block.content[0]}\n"

    response = process_autoreview_request(text)
    parsed_response = parse_result(response)
    colab.colab_res["errors"] = parsed_response.get("errors")
    colab.colab_res["status"] = parsed_response.get("status")

    return colab
