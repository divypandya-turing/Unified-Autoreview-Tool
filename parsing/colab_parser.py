"""This script contains class that handles the complete Colab Info."""

from parsing.block_parser import (
    RTU,
    BaseBlock,
    Code,
    CodeOutput,
    DocRelevanceRetrieval,
    DocRelevanceRetrievalOut,
    ICEFileMetadata,
    ReWrittenQuery,
    Thought,
    ToolCode,
    ToolOutput,
    UserQuery,
)
from parsing.plan_parser_utils import get_closest_match
from parsing.turn import Turn
from utils import EVENTS_TAG_UNIQUE_COLAB

MAPPER: dict[str, BaseBlock] = {
    "USER_QUERY:": UserQuery,
    "ICE_FILE_METADATA:": ICEFileMetadata,
    "DOC_RELEVANCE_RETRIEVAL:": DocRelevanceRetrieval,
    "DOC_RELEVANCE_RETRIEVAL_OUT:": DocRelevanceRetrievalOut,
    "REWRITTEN_QUERY:": ReWrittenQuery,
    "TOOL_CODE:": ToolCode,
    "TOOL_OUTPUT:": ToolOutput,
    "CODE:": Code,
    "CODE_OUTPUT:": CodeOutput,
    "THOUGHT:": Thought,
    "RESPONSE_TO_USER:": RTU,
}


class ColabPlanParser:
    """
    A class representing the entire Colab plan and its sections, supporting multi-turn parsing.

    Attributes
    ----------
    plan (str): The input plan string.
    turns (list): A list of turns, each containing its own sections.
    """

    def __init__(self, plan: str, sft_type: str, is_stepwise: bool):
        """
        Initializes a ColabPlanParser instance.

        Parameters
        ----------
        plan (str): The input plan string.
        """
        self.plan: str = plan
        self.sft_type: str = sft_type
        self.is_stepwise: bool = is_stepwise
        self.turns: list[Turn] = []
        self.parse_plan()  # Automatically parse the plan during initialization

    def parse_plan(self):
        """
        Parses the plan into multiple turns and sections, handling typos in both block tags and sub-tags.
        """
        # Initialize the current turn as an empty list
        turn_num = 1
        current_turn = Turn(idx=turn_num, sft_type=self.sft_type, is_stepwise=self.is_stepwise)
        # Initialize serial number for the first section
        serial_number = 1
        # Track the current block
        current_block = None

        # Iterate over each cell (tuple of (cell_type, cell_content)) in the plan
        for cell_num, (cell_type, cell_content) in enumerate(self.plan, start=1):
            # Clean up the cell content
            cell_content = cell_content.strip()
            # if not cell_content:
            #     continue

            # Process markdown cells line by line
            if cell_type == "markdown":
                current_block = None
                # Split the markdown content into individual lines
                markdown_lines = cell_content.split("\n")

                for markdown_line in markdown_lines:
                    markdown_line = markdown_line.strip()
                    if not markdown_line:
                        continue

                    # Split the line into words to find potential tags
                    if ":" in markdown_line:
                        words = []
                        for i, word in enumerate(markdown_line.split(":")):
                            if i % 2 == 0:
                                words.append(word + ":")
                            else:
                                words.append(word)

                    else:
                        words = markdown_line.split()
                    max_words = min(len(words), 5)  # Limit the number of words for matching
                    potential_tag = candidate_tag = ""
                    content = []

                    # Iterate over the first 5 words to find the longest valid tag
                    for i in range(max_words):
                        # Create a candidate tag by joining the first i+1 words
                        candidate_tag = " ".join(words[: i + 1])
                        closest_tag = get_closest_match(candidate_tag, EVENTS_TAG_UNIQUE_COLAB)

                        if closest_tag:
                            potential_tag = candidate_tag
                            # The rest of the line is treated as content
                            content.append(" ".join(words[i + 1 :]))  # noqa: E203
                            break  # Stop after finding the first matching tag

                    if closest_tag == "TURN:" and cell_num == 1:
                        continue

                    if closest_tag == "TURN:":
                        self.turns.append(current_turn)
                        turn_num += 1
                        current_turn = Turn(
                            idx=turn_num,
                            sft_type=self.sft_type,
                            is_stepwise=self.is_stepwise,
                        )
                        serial_number = 1
                        continue

                    # Handle the matched tag
                    if closest_tag:
                        # If a valid tag is found, start a new block
                        current_block = MAPPER[closest_tag](
                            self.sft_type, serial_number, potential_tag, closest_tag, content
                        )
                        current_turn.add_block(current_block)
                        serial_number += 1
                    else:
                        # # No valid tag, append content to the current block
                        if current_block:
                            current_block.content.append(markdown_line)
                        else:
                            # Start a new block if none exists
                            candidate_tag = "MISSING_TAG:" if len(candidate_tag.split()) > 3 else candidate_tag
                            current_block = BaseBlock(
                                self.sft_type,
                                serial_number,
                                candidate_tag,
                                "MISSING_TAG:",
                                [markdown_line],
                            )
                            current_turn.add_block(current_block)
                            serial_number += 1

            # Process code cells
            elif cell_type == "code":
                # Handle code cell as a separate block
                current_block = Code(self.sft_type, serial_number, "CODE:", "CODE:", [cell_content])
                current_turn.add_block(current_block)
                serial_number += 1

            # Process code output cells
            elif cell_type == "code_output":
                # Handle code output cell as a separate block
                current_block = CodeOutput(self.sft_type, serial_number, "CODE_OUTPUT:", "CODE_OUTPUT:", [cell_content])
                current_turn.add_block(current_block)
                serial_number += 1

        # Append the last turn if present
        if current_turn.blocks:
            self.turns.append(current_turn)

        self.num_code_errors = 0
        for turn in self.turns:
            turn.parse_blocks()
            turn.parse_datasets()
            self.num_code_errors += turn.num_code_errors()

    def get_turns(self):
        """
        Retrieves all parsed turns.

        Returns
        -------
        list: A list of turns, where each turn is a list of Section objects.
        """
        return self.turns
