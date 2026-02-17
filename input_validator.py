"""
input_validator.py

A small utility module for validating user input.
"""

class ValidationError(Exception):
    """Custom exception for invalid input."""
    pass


def validate_int(value, min_val=None, max_val=None):
    """
    Validate that value can be converted to an int and falls within a range.

    :param value: input value (usually string)
    :param min_val: minimum allowed integer (inclusive)
    :param max_val: maximum allowed integer (inclusive)
    :return: validated int
    """
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise ValidationError("Input must be an integer.")
    if min_val is not None and value < min_val:
        raise ValidationError(f"Input must be >= {min_val}.")

    if max_val is not None and value > max_val:
        raise ValidationError(f"Input must be <= {max_val}.")

    return value


def validate_float(value, min_val=None, max_val=None):
    """
    Validate that value can be converted to a float and falls within a range.
    """
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValidationError("Input must be a number.")

    if min_val is not None and value < min_val:
        raise ValidationError(f"Input must be >= {min_val}.")

    if max_val is not None and value > max_val:
        raise ValidationError(f"Input must be <= {max_val}.")

    return value


def validate_string(value, allowed=None, case_sensitive=False):
    """
    Validate a string against allowed values.

    :param value: input value
    :param allowed: list/set of allowed strings (None = any string allowed)
    :param case_sensitive: whether matching should be case-sensitive
    :return: validated string
    """
    if not isinstance(value, str):
        raise ValidationError("Input must be a string.")

    if allowed is not None:
        if not case_sensitive:
            value_cmp = value.lower()
            allowed_cmp = [a.lower() for a in allowed]
        else:
            value_cmp = value
            allowed_cmp = allowed

        if value_cmp not in allowed_cmp:
            raise ValidationError(f"Input must be one of: {allowed}")

    return value


def validate_char(value, allowed=None, case_sensitive=False):
    """
    Validate a single character.

    :param value: input value
    :param allowed: list/set of allowed characters
    :return: validated character
    """
    value = value.strip()
    if not isinstance(value, str) or len(value) != 1:
        raise ValidationError("Input must be a single character.")

    return validate_string(value, allowed, case_sensitive)


def validate_input(value, expected_type, **kwargs):
    """
    Generic validator dispatcher.

    :param value: input value
    :param expected_type: int, float, str, or 'char'
    :param kwargs: validation options (min_val, max_val, allowed, etc.)
    :return: validated value
    """
    if expected_type == int:
        return validate_int(value, **kwargs)
    elif expected_type == float:
        return validate_float(value, **kwargs)
    elif expected_type == str:
        return validate_string(value, **kwargs)
    elif expected_type == "char":
        return validate_char(value, **kwargs)
    else:
        raise ValidationError("Unsupported type.")