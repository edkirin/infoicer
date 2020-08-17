from collections import OrderedDict

import json
from typing import Union, List

from .util import *

ZERO = quanitize(Decimal(0))


#**************************************************************************************************


class CustomJsonEncoder(json.JSONEncoder):

    #----------------------------------------------------------------------------------------------

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(CustomJsonEncoder, self).default(obj)

    #----------------------------------------------------------------------------------------------


#**************************************************************************************************


class InvoiceItem:
    caption: str = None
    item_type: str = None
    tax_rate: Decimal = None
    net_amount: Decimal = None  # single product price
    amount: Decimal = None  # single product price
    tax_amount: Decimal = None  # single product price
    storno: bool = False
    qty: int = 1
    obj: object = None
    discount_enabled: bool = False
    _decimal_places: int = 2

    #----------------------------------------------------------------------------------------------

    def __init__(
            self,
            name: str,
            item_type: str,
            qty: int = 1,
            net_amount: Union[Decimal, None] = None,
            tax_rate: Union[Decimal, None] = ZERO,
            tax_amount: Union[Decimal, None] = ZERO,
            amount: Union[Decimal, None] = None,
            storno: bool = False,
            obj: object = None,
    ):
        self.name = name
        self.item_type = item_type
        self.qty = qty
        self.tax_rate = tax_rate
        self.tax_amount = tax_amount
        self.storno = storno
        self.obj = obj

        if amount is not None:
            self.set_amount(amount)
        if net_amount is not None:
            self.set_net_amount(net_amount)

    #----------------------------------------------------------------------------------------------

    def set_net_amount(self, value: Decimal):
        self.net_amount = value
        self.amount, self.tax_amount = nett_to_brutto(value, self.tax_rate)

    #----------------------------------------------------------------------------------------------

    def set_amount(self, value: Decimal):
        self.amount = value
        self.net_amount, self.tax_amount = brutto_to_nett(value, self.tax_rate)

    #----------------------------------------------------------------------------------------------

    def __str__(self):
        return "[{item_type}] {qty}x {name} {amount} (tax {tax_rate}%: {nett} + {tax})".format(
            item_type=self.item_type,
            qty=self.qty,
            name=self.name,
            amount=self.get_amount_sum(),
            tax_rate=self.tax_rate,
            nett=self.get_net_amount_sum(),
            tax=self.get_tax_sum(),
        )

    #----------------------------------------------------------------------------------------------

    def get_net_amount_sum(self) -> Decimal:
        return quanitize(self.net_amount * self.qty, decimal_places=self._decimal_places)

    #----------------------------------------------------------------------------------------------

    def get_amount_sum(self) -> Decimal:
        return quanitize(self.amount * self.qty, decimal_places=self._decimal_places)

    #----------------------------------------------------------------------------------------------

    def get_tax_sum(self) -> Decimal:
        return quanitize(self.tax_amount * self.qty, decimal_places=self._decimal_places)

    #----------------------------------------------------------------------------------------------

    def serialize(self) -> dict:
        return {
            'item_type': self.item_type,
            'qty': self.qty,
            'name': self.name,
            'amount': self.get_amount_sum(),
            'tax_rate': self.tax_rate,
            'nett': self.get_net_amount_sum(),
            'tax': self.get_tax_sum(),
        }

    #----------------------------------------------------------------------------------------------


#**************************************************************************************************


class InvoiceItemContainer(list):
    tax_rate: Decimal = None

    #----------------------------------------------------------------------------------------------

    def __init__(self, tax_rate: Decimal):
        super().__init__()
        self.tax_rate = tax_rate

    #----------------------------------------------------------------------------------------------

    def __str__(self):
        res = [f"Invoice container for tax rate {self.tax_rate}"]
        res += [str(c) for c in self]
        return '\n'.join(res)

    #----------------------------------------------------------------------------------------------

    def append(self, item: InvoiceItem):
        super().append(item)

    #----------------------------------------------------------------------------------------------

    def get_net_amount_sum(self):
        return sum([c.get_net_amount_sum() for c in self])

    #----------------------------------------------------------------------------------------------

    def get_amount_sum(self):
        return sum([c.get_amount_sum() for c in self])

    #----------------------------------------------------------------------------------------------

    def get_tax_sum(self):
        return sum([c.get_tax_sum() for c in self])

    #----------------------------------------------------------------------------------------------

    def find_item(self, name: str, amount: Decimal, item_type: str = None):
        for item in self:
            # take item_type in comparison only if not None
            if (
                    item.name == name and item.amount == amount and item_type is None
            ) or (
                    item.name == name and item.amount == amount and item.item_type == item_type
            ):
                return item
        return None

    #----------------------------------------------------------------------------------------------


#**************************************************************************************************


class Invoice:
    containers: List[InvoiceItemContainer] = None
    decimal_places: int = 2

    #----------------------------------------------------------------------------------------------

    def __init__(self, decimal_places: int = 2):
        self.containers = list()
        self.decimal_places = decimal_places

    #----------------------------------------------------------------------------------------------

    def __str__(self):
        res = [str(c) for c in self.containers]

        res.extend([
            '----------------',
            f"Amount      : {self.get_amount_sum():>10}",
            f"Net amount  : {self.get_net_amount_sum():>10}",
            f"Tax amount  : {self.get_tax_sum():>10}",
        ])

        return '\n'.join(res)

    #----------------------------------------------------------------------------------------------

    def add(self, item: InvoiceItem):
        item._decimal_places = self.decimal_places

        for container in self.containers:
            if container.tax_rate == item.tax_rate:
                existing_item = container.find_item(
                    name=item.name,
                    amount=item.amount,
                    item_type=item.item_type,
                )
                if existing_item is not None:
                    if existing_item.amount == item.amount:
                        existing_item.qty += item.qty
                    else:
                        existing_item.amount += item.amount * item.qty
                else:
                    container.append(item)
                return

        container = InvoiceItemContainer(tax_rate=item.tax_rate)
        self.containers.append(container)
        container.append(item)

    #----------------------------------------------------------------------------------------------

    def get_amount_sum(self, item_type: str = None) -> Decimal:
        return sum([c.get_amount_sum() for c in self.get_all_items(item_type=item_type)])

    #----------------------------------------------------------------------------------------------

    def get_net_amount_sum(self, item_type: str = None) -> Decimal:
        return sum([c.get_net_amount_sum() for c in self.get_all_items(item_type=item_type)])

    #----------------------------------------------------------------------------------------------

    def get_tax_sum(self, item_type: str = None) -> Decimal:
        return sum([c.get_tax_sum() for c in self.get_all_items(item_type=item_type)])

    #----------------------------------------------------------------------------------------------

    def get_all_items(self, item_type: Union[str, List] = None) -> List[InvoiceItem]:
        res = list()

        if item_type is not None and not isinstance(item_type, list):
            item_type = [item_type]

        for container in self.containers:
            if item_type is None:
                res.extend(container)
            else:
                for c in container:
                    if c.item_type in item_type:
                        res.append(c)
        return res

    #----------------------------------------------------------------------------------------------

    def get_items_count(self, item_type: str = None, calc_storno: bool = True) -> int:
        sold_qty = storno_qty = 0
        for item in self.get_all_items(item_type=item_type):
            if not item.storno:
                sold_qty += item.qty
            else:
                storno_qty += item.qty
        return sold_qty - storno_qty if calc_storno else sold_qty + storno_qty

    #----------------------------------------------------------------------------------------------

    def group_by_tax_rate(self, item_type: str = None) -> list:
        tax_rates = OrderedDict()

        for item in self.get_all_items(item_type=item_type):
            if item.tax_rate in tax_rates:
                d = tax_rates[item.tax_rate]
            else:
                d = {
                    'tax_rate': item.tax_rate,
                    'items': list(),
                    'amount': ZERO,
                    'nett': ZERO,
                    'tax': ZERO,
                }
                tax_rates.update({
                    item.tax_rate: d,
                })

            d['items'].append(item.serialize())
            d['amount'] += item.get_amount_sum()
            d['nett'] += item.get_net_amount_sum()
            d['tax'] += item.get_tax_sum()

        return list(tax_rates.values())

    #----------------------------------------------------------------------------------------------

    def serialize(self, item_type: str = None, json_output: bool = False) -> Union[dict, str]:
        res = {
            'tax_rates': OrderedDict(),
            'total': {
                'amount': 0,
                'nett': 0,
                'tax': 0,
            },
        }

        for item in self.get_all_items(item_type=item_type):
            if item.tax_rate in res['tax_rates']:
                d = res['tax_rates'][item.tax_rate]
            else:
                d = {
                    'items': list(),
                    'amount': 0,
                    'nett': 0,
                    'tax': 0,
                }
                res['tax_rates'].update({item.tax_rate: d})

            amount = item.get_amount_sum()
            nett = item.get_net_amount_sum()
            tax = item.get_tax_sum()
            d['items'].append(item.serialize())
            d['amount'] += amount
            d['nett'] += nett
            d['tax'] += tax
            res['total']['amount'] += amount
            res['total']['nett'] += nett
            res['total']['tax'] += tax

        if json_output:
            res = json.dumps(res, cls=CustomJsonEncoder)

        return res

    #----------------------------------------------------------------------------------------------


#**************************************************************************************************
