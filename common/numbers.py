"""
Helper module to deal with numbers
"""

import decimal


def truncate_decimal_2(value):
    """
    Truncate value to 2 places decimal without rounding
    """
    return decimal.Decimal(value).quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_DOWN)
