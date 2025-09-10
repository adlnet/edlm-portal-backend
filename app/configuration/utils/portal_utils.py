import logging

from confusable_homoglyphs import categories, confusables

logger = logging.getLogger(__name__)


def confusable_homoglyphs_check(data):
    """Checks for dangerous homoglyphs."""

    data_is_safe = True
    for key in data:

        # if string, Check homoglyph
        if isinstance(data[key], str) and bool(confusables.
                                               is_dangerous(data[key])):
            data_is_safe = False
            logger.error(categories.unique_aliases(data[key]))
        # if dict, enter dict
        if isinstance(data[key], dict):
            ret_val = confusable_homoglyphs_check(data[key])
            if not ret_val:
                data_is_safe = False
    return data_is_safe
