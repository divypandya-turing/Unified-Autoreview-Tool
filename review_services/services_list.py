"""This file contains Validator list."""

from review_services.autoreview_spelling_grammar import spell_grammar_autoreview
from review_services.sft_validator import sft_validator

VALIDATOR_LIST = {
    "SFT Validator": sft_validator,
    "AutoReview Spelling and Grammar": spell_grammar_autoreview,
}
