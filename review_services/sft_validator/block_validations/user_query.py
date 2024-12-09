"""This script contains validation checks for the USER_QUERY."""


from review_services.sft_validator.block_validations import BaseBlockValidators


class UserQueryValidators(BaseBlockValidators):
    """
    This class handles validations for the USER_QUERY block.
    """

    def validate(self) -> list[list]:
        """
        Run all block-specific validations.

        Returns
        ------
        List[str]
            A list of failed check IDs.
        """
        checks = [
            self.has_typo_in_tag,
            self.validate_content_exists,
        ]

        failed_checks = []
        for check in checks:
            check_id = check()
            if check_id:
                failed_checks.append(check_id)

        return failed_checks
