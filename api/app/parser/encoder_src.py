import numpy as np


def EncoderSrcParser(input_string):
    """
    Convert a string into its binary representation based on ASCII codes.

    Args:
        input_string (str): The string to convert.

    Returns:
        str: A binary string representation of the input string.
    """
    return ''.join(format(ord(char), '08b') for char in input_string)