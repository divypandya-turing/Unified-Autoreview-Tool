"""This script contains class that handles the Turn info."""


from parsing.block_parser import BaseBlock


class Turn:
    """This class handles the Turn info."""

    def __init__(self, idx: int, sft_type: str, is_stepwise: bool):
        self.idx = idx
        self.sft_type = sft_type
        self.is_stepwise = is_stepwise
        self.blocks: list[BaseBlock] = []
        self.datasets: dict[str, str] = {}
        self.skip_rows_count: dict[str, int] = {}

    def add_block(self, block: BaseBlock) -> None:
        """
        Adds a block to the turn.

        Parameters
        ----------
        block (BaseBlock): The block to be added to the turn.
        """
        self.blocks.append(block)

    def parse_blocks(self):
        """This method parses the blocks by calling the parse_block method of each block."""
        for block in self.blocks:
            block.parse_block()

    def num_code_errors(self):
        """This method returns the number of code errors in the turn."""
        num_code_errors = 0
        for block in self.blocks:
            if block.matched_tag == "CODE_OUTPUT:":
                if block.has_code_error:
                    num_code_errors += 1
        return num_code_errors

    def parse_datasets(self):
        """This method extracts file name, url and estimated_rows_above_header from
        the ICE_FILE_METADATA and TOOL_OUTPUT blocks.
        """
        for block in self.blocks:
            if block.matched_tag == "ICE_FILE_METADATA:":
                if block.metadata:
                    file_name = block.metadata.get("file_name:", {}).get("value", "")
                    file_path = block.metadata.get("FILE_PATH:", {}).get("value", "")
                    if file_name.endswith((".csv", ".tsv", ".pdf")):
                        self.datasets.update({file_name: file_path})

                    skip_rows_count = block.metadata.get("estimated_rows_above_header:", {}).get("value", None)
                    if skip_rows_count:
                        self.skip_rows_count.update({file_name: int(skip_rows_count)})

            elif block.matched_tag == "TOOL_OUTPUT:":
                if block.metadata:
                    tool_dict = block.metadata.get("code_generated_text_files", {})
                    file_name = tool_dict.get("file_name", "")
                    file_path = tool_dict.get("file_attachment", {}).get("serving_url", "")
                    if file_name.endswith((".csv", ".tsv", ".pdf")):
                        self.datasets.update({file_name: file_path})

    def __str__(self):
        print(f"Turn {self.idx}:")  # noqa: T201
        for block in self.blocks:
            print(block)  # noqa: T201
        return ""
