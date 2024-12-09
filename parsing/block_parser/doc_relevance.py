"""This script contains DOC_RELEVANCE_RETRIEVAL, DOC_RELEVANCE_RETRIEVAL_OUT and REWRITTEN_QUERY parsing classes."""

from parsing.block_parser import BaseBlock


class DocRelevanceRetrieval(BaseBlock):
    """
    A class representing the DOC_RELEVANCE_RETRIEVAL in the plan.

    Attributes
    ----------
    serial_number (int): The serial number of the block.

    original_tag (str): The original tag as found in the input (including typos if any).

    matched_tag (str): The closest valid tag matched with the list of event tags.

    content (str): The raw content associated with the block (excluding the tag name).

    """


class DocRelevanceRetrievalOut(BaseBlock):
    """
    A class representing the DOC_RELEVANCE_RETRIEVAL_OUT in the plan.

    Attributes
    ----------
    serial_number (int): The serial number of the block.

    original_tag (str): The original tag as found in the input (including typos if any).

    matched_tag (str): The closest valid tag matched with the list of event tags.

    content (str): The raw content associated with the block (excluding the tag name).

    """


class ReWrittenQuery(BaseBlock):
    """
    A class representing the REWRITTEN_QUERY in the plan.

    Attributes
    ----------
    serial_number (int): The serial number of the block.

    original_tag (str): The original tag as found in the input (including typos if any).

    matched_tag (str): The closest valid tag matched with the list of event tags.

    content (str): The raw content associated with the block (excluding the tag name).

    """
