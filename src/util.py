from decimal import Decimal, ROUND_HALF_UP


#--------------------------------------------------------------------------------------------------


def quanitize(value: Decimal, decimal_places: int = 2) -> Decimal:
    return value.quantize(Decimal(f'0.{"0" * decimal_places}'), ROUND_HALF_UP)


#--------------------------------------------------------------------------------------------------


def nett_to_brutto(value: Decimal, tax_rate: Decimal):
    tax_amount = quanitize(value * tax_rate / Decimal(100.0))
    brutto = value + tax_amount
    return brutto, tax_amount


#--------------------------------------------------------------------------------------------------


def brutto_to_nett(value: Decimal, tax_rate: Decimal):
    nett = quanitize(value / (Decimal(1.0) + tax_rate / Decimal(100.0)))
    tax_amount = value - nett
    return nett, tax_amount


#--------------------------------------------------------------------------------------------------
