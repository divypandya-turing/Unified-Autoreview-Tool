"""This file contains function that runs the SFT validator on a Colab file."""

from review_services.colab import Colab
from review_services.sft_validator.sft_consts import OnlineSFTCodeErrors
from review_services.sft_validator.turn_validations import TurnValidators
from utils import Status


def sft_validator(file_info: dict[str, str]) -> Colab:
    """Function to process a single Colab file.

    Parameters
    ----------
    file_info : dict[str, str]
        Dictionary containing the file information

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

    all_turn_checks, total_turns = [], len(colab.parsed_colab.get_turns())
    for turn in colab.parsed_colab.get_turns():
        turn_validator = TurnValidators(turn)

        # Call the validation function for the entire turn
        failed_checks = turn_validator.validate_turn(total_turns)
        all_turn_checks.extend(failed_checks)

    if colab.parsed_colab.num_code_errors > 0 and colab.file_name not in OnlineSFTCodeErrors.res_dict:
        all_turn_checks.append(
            [
                None,
                None,
                f"The colab has {colab.parsed_colab.num_code_errors}"
                "code error but missing from the code error tracker.",
            ]
        )

    if (
        colab.file_name in OnlineSFTCodeErrors.res_dict
        and OnlineSFTCodeErrors.res_dict[colab.file_name] != colab.parsed_colab.num_code_errors
    ):
        num_errors = colab.parsed_colab.num_code_errors
        expected_num_errors = OnlineSFTCodeErrors.res_dict.get(colab.file_name, 0)
        all_turn_checks.append(
            [
                None,
                None,
                f"The colab has {num_errors} code errors but code error tracker has {expected_num_errors} errors.",
            ]
        )

    if all_turn_checks:
        colab.colab_res["errors"] = all_turn_checks
        colab.colab_res["status"] = Status.FAILED
    else:
        colab.colab_res["errors"] = None
        colab.colab_res["status"] = Status.PASSED

    return colab
