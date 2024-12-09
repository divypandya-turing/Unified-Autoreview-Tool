"""This script contains class that handles validations for the RESPONSE_TO_USER block."""

from review_services.sft_validator.block_validations import BaseBlockValidators


class RTUValidators(BaseBlockValidators):
    """
    This class handles validations for the RESPONSE_TO_USER block.
    """

    def validate(self) -> list[list]:
        """
        Run all RTU-specific validations.

        Returns
        ------
        List[str]
            A list of failed check IDs.
        """
        checks = [
            self.has_typo_in_tag,
            self.validate_content_exists,
            # self.has_smart_quotes,
        ]

        failed_checks = []
        for check in checks:
            check_id = check()
            if check_id:
                failed_checks.append(check_id)

        return failed_checks
