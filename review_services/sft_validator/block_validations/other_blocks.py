"""This script contains class that handles validations for other misc blocks."""

from review_services.sft_validator.block_validations import BaseBlockValidators


class OtherBlockValidators(BaseBlockValidators):
    """This class handles validations for blocks other than above."""

    def validate(self) -> list[list]:
        """Run all the validators.

        Returns
        -------
        list[list]
            A list of failed check IDs.
        """
        checks = [self.has_typo_in_tag, self.validate_content_exists]

        failed_checks = []
        for check in checks:
            check_id = check()
            if check_id:
                failed_checks.append(check_id)

        return failed_checks
