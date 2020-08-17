from decimal import Decimal, ROUND_HALF_UP


#--------------------------------------------------------------------------------------------------


def quanitize(value: Decimal, decimal_places: int = 2) -> Decimal:
    return value.quantize(Decimal(f'0.{"0" * decimal_places}'), ROUND_HALF_UP)


#--------------------------------------------------------------------------------------------------


def net_to_gross(value: Decimal, tax_rate: Decimal, decimal_places: int = 2):
    tax_amount = quanitize(value * tax_rate / Decimal(100.0), decimal_places=decimal_places)
    gross = value + tax_amount
    return gross, tax_amount


#--------------------------------------------------------------------------------------------------


def gross_to_net(value: Decimal, tax_rate: Decimal, decimal_places: int = 2):
    net = quanitize(value / (Decimal(1.0) + tax_rate / Decimal(100.0)), decimal_places=decimal_places)
    tax_amount = value - net
    return net, tax_amount


#--------------------------------------------------------------------------------------------------
