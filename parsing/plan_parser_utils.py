"""This file contains functions to parse plan into sections."""

import difflib


def get_closest_match(item: str, valid_items: list[str]) -> str:
    """
    Finds the closest matching item (block tag or sub-tag) from the provided list of valid items.

    Parameters
    ----------
    item (str): The item (block tag or sub-tag) that needs to be matched.
    valid_items (list): The list of valid items to match against.

    Returns
    -------
    str: The closest valid item if a match is found, otherwise returns the original item.
    """
    # Convert both the input item and valid items to lowercase for comparison
    item_lower = item.lower()
    valid_item_map = {v.lower(): v for v in valid_items}  # Map lowercase items to their original form

    # Check if there's a case-insensitive match
    if item_lower in valid_item_map:
        return valid_item_map[item_lower]

    # Apply typo correction if no direct match is found
    closest_match = difflib.get_close_matches(item_lower, list(valid_item_map.keys()), n=1, cutoff=0.8)
    return valid_item_map[closest_match[0]] if closest_match else None
