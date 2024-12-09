"""This script contains class that handles all the Turn level validation checks."""

from parsing import Turn
from review_services.sft_validator.block_validations import (
    CODEOutputValidators,
    CODEValidator,
    ICEFileMetadataValidators,
    OtherBlockValidators,
    RTUValidators,
    ThoughtValidators,
    UserQueryValidators,
)
from review_services.sft_validator.sft_consts import BaseSFTSequence, FileSFTSequence, PDFSFTSequence


class TurnValidators:
    """
    Handles validation across multiple blocks within a turn.
    """

    def __init__(self, turn: Turn):
        """
        Initialize the TurnValidators instance.

        Parameters
        ----------
        blocks (list): A list of BaseBlock instances representing all blocks in a turn.
        """
        self.turn: Turn = turn
        self.blocks = self.turn.blocks
        # Initialize block validators for each block
        self.block_validators = []
        for block in self.blocks:
            if block.matched_tag == "USER_QUERY:":
                self.block_validators.append(UserQueryValidators(block, turn.idx))
            elif block.matched_tag == "ICE_FILE_METADATA:":
                self.block_validators.append(ICEFileMetadataValidators(block, turn.idx))
            elif block.matched_tag == "THOUGHT:":
                self.block_validators.append(ThoughtValidators(block, turn.idx, turn.datasets))
            elif block.matched_tag == "RESPONSE_TO_USER:":
                self.block_validators.append(RTUValidators(block, turn.idx))
            elif block.matched_tag == "CODE:":
                self.block_validators.append(CODEValidator(block, turn.idx, turn.datasets, turn.skip_rows_count))
            elif block.matched_tag == "CODE_OUTPUT:":
                self.block_validators.append(CODEOutputValidators(block, turn.idx))
            else:
                self.block_validators.append(OtherBlockValidators(block, turn.idx))

        self.__msg = [turn.idx]

    def validate_sequence(self, total_turns: int) -> list:
        """
        Validates the sequence of blocks in the turn, allowing 'ICE_FILE_METADATA:' to appear
        consecutively any number of times between 'USER_QUERY' and 'THOUGHT'.

        Parameters
        ----------
        total_turns (int): number of total turns.

        Returns
        -------
        list: A list of error messages indicating any sequence mismatches found during validation.
        """

        # Index to track the initial sequence
        initial_seq_index = 0
        block_index = 0  # Track how far we've gone in the blocks list
        # Define the initial sequence, including ICE_FILE_METADATA, which can appear multiple times
        failed_checks = []
        initial_sequence = repeating_cycle = []

        if self.turn.sft_type in ["file", "marketing"]:
            initial_sequence = FileSFTSequence.init_seq
            repeating_cycle = FileSFTSequence.repeating_seq

        elif self.turn.sft_type == "pdf":
            initial_sequence = PDFSFTSequence.init_seq
            repeating_cycle = PDFSFTSequence.repeating_seq

        elif self.turn.sft_type in ["no_file", "reasoning", "search", "browse"]:
            initial_sequence = BaseSFTSequence.init_seq
            repeating_cycle = BaseSFTSequence.repeating_seq

        # Validate the initial sequence, ensuring the loop progresses
        while initial_seq_index < len(initial_sequence) and block_index < len(self.blocks):
            expected_tag = initial_sequence[initial_seq_index]
            current_block = self.blocks[block_index]

            # Handle flexible ICE_FILE_METADATA occurrences
            if expected_tag == "ICE_FILE_METADATA:":
                # Allow multiple ICE_FILE_METADATA blocks in a row
                if current_block.matched_tag == "ICE_FILE_METADATA:":
                    # Keep moving through the blocks
                    block_index += 1
                else:
                    # Move to the next expected tag if not ICE_FILE_METADATA
                    initial_seq_index += 1
            else:
                # Validate the block matches the expected tag
                if current_block.matched_tag != expected_tag:
                    failed_checks.append(
                        self.__msg
                        + [
                            current_block.serial_number,
                            "SEQUENCE_MISMATCH: Expected '{expected_tag}'" f" but got '{current_block.original_tag}'",
                        ]
                    )
                block_index += 1
                initial_seq_index += 1

        # Validate the repeating cycle after the initial sequence
        current_step = 0
        if repeating_cycle and block_index < len(self.blocks):
            for block in self.blocks[block_index:-1]:
                if block.matched_tag != repeating_cycle[current_step]:
                    failed_checks.append(
                        self.__msg
                        + [
                            block.serial_number,
                            f"SEQUENCE_MISMATCH: Expected "
                            f"'{repeating_cycle[current_step]}'"
                            f" but got '{block.original_tag}'",
                        ]
                    )
                current_step = (current_step + 1) % len(repeating_cycle)

        # Dynamic checks for specific conditions
        thought_count = 0
        for i in range(1, len(self.blocks)):
            current_block = self.blocks[i]
            previous_block = self.blocks[i - 1]

            # Ensure CODE is always followed by CODE_OUTPUT
            if previous_block.matched_tag == "CODE:" and current_block.matched_tag != "CODE_OUTPUT:":
                failed_checks.append(
                    self.__msg
                    + [block.serial_number, "SEQUENCE_MISMATCH: 'CODE:' " "must be followed by 'CODE_OUTPUT:'"]
                )

            # Ensure TOOL_OUTPUT is preceded by TOOL_CODE
            if current_block.matched_tag == "TOOL_OUTPUT:" and previous_block.matched_tag != "TOOL_CODE:":
                failed_checks.append(
                    self.__msg
                    + [block.serial_number, "SEQUENCE_MISMATCH: 'TOOL_OUTPUT:' " "must be preceded by 'TOOL_CODE:'"]
                )

            # Ensure DOC_RELEVANCE_RETRIEVAL is followed by DOC_RELEVANCE_RETRIEVAL_OUT and REWRITTEN_QUERY
            if current_block.matched_tag == "DOC_RELEVANCE_RETRIEVAL:":
                if i + 1 < len(self.blocks) and self.blocks[i + 1].matched_tag != "DOC_RELEVANCE_RETRIEVAL_OUT:":
                    failed_checks.append(
                        self.__msg
                        + [
                            block.serial_number,
                            "SEQUENCE_MISMATCH: 'DOC_RELEVANCE_RETRIEVAL:' "
                            "must be followed by 'DOC_RELEVANCE_RETRIEVAL_OUT:'",
                        ]
                    )
                if i + 2 < len(self.blocks) and self.blocks[i + 2].matched_tag != "REWRITTEN_QUERY:":
                    failed_checks.append(
                        self.__msg
                        + [
                            block.serial_number,
                            "SEQUENCE_MISMATCH: 'DOC_RELEVANCE_RETRIEVAL:' "
                            "must be followed by 'DOC_RELEVANCE_RETRIEVAL_OUT:' and 'REWRITTEN_QUERY:'",
                        ]
                    )

            # Ensure THOUGHT never comes after RESPONSE_TO_USER
            if current_block.matched_tag == "THOUGHT:" and previous_block.matched_tag == "RESPONSE_TO_USER:":
                failed_checks.append(
                    self.__msg
                    + [block.serial_number, "SEQUENCE_MISMATCH: 'THOUGHT:' " "must not come after 'RESPONSE_TO_USER:'"]
                )

            # Ensure that every THOUGHT after the first is immediately followed by RESPONSE_TO_USER
            if current_block.matched_tag == "THOUGHT:":
                thought_count += 1
                if thought_count > 1:
                    # Check if the next block exists and is not RESPONSE_TO_USER
                    if i + 1 >= len(self.blocks) or self.blocks[i + 1].matched_tag != "RESPONSE_TO_USER:":
                        failed_checks.append(
                            self.__msg
                            + [
                                block.serial_number,
                                "SEQUENCE_MISMATCH: 'THOUGHT:' " "must be followed by 'RESPONSE_TO_USER:'",
                            ]
                        )

        last_block = self.blocks[-1]
        # If it's a stepwise SFT, Ensure the last block is RESPONSE_TO_USER: or CODE_OUTPUT:
        if self.turn.is_stepwise:

            if self.turn.idx == total_turns and last_block.matched_tag == "RESPONSE_TO_USER:":
                failed_checks.append(
                    self.__msg
                    + [
                        block.serial_number,
                        "SEQUENCE_MISMATCH: Found 'RESPONSE_TO_USER:' at the end of the Stepwise SFT.",
                    ]
                )

            elif last_block.matched_tag not in [
                "RESPONSE_TO_USER:",
                "CODE_OUTPUT:",
            ]:
                failed_checks.append(
                    self.__msg
                    + [
                        block.serial_number,
                        "SEQUENCE_MISMATCH: Expected last block to be 'RESPONSE_TO_USER: or CODE_OUTPUT:'"
                        f" but got '{last_block.original_tag}'",
                    ]
                )

        # If it's a non-stepwise SFT, Ensure the last block is RESPONSE_TO_USER:
        elif not self.turn.is_stepwise and last_block.matched_tag != "RESPONSE_TO_USER:":
            failed_checks.append(
                self.__msg
                + [
                    block.serial_number,
                    "SEQUENCE_MISMATCH: Expected last block to be 'RESPONSE_TO_USER:'"
                    f" but got '{last_block.original_tag}'",
                ]
            )

        return failed_checks

    def validate_turn(self, total_turns: int) -> list:
        """
        Runs all turn-level validations.

        Parameters
        ----------

        total_turns (int): number of total turns.

        Returns
        -------
        list: A list of failed check IDs.
        """
        failed_checks = []

        # Run block-level validation for each block
        for block_validator in self.block_validators:
            failed_checks.extend(block_validator.validate())

        # Run sequence validation
        failed_checks.extend(self.validate_sequence(total_turns))
        return failed_checks
