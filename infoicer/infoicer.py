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
    """InvoiceItem object contains all relevant data for single invoice item. `net_price` or
    `price` can be set during creation of the class, or later with methods `InvoiceItem.set_net_price()`
    and `InvoiceItem.set_price()`
    """

    caption: str = None
    item_type: str = None
    tax_rate: Decimal = None
    net_price: Decimal = None  # single product price
    price: Decimal = None  # single product price
    tax_amount: Decimal = ZERO  # single product price
    qty: int = 1
    obj: object = None
    decimal_places: int = 2

    #----------------------------------------------------------------------------------------------

    def __init__(
            self,
            name: str,
            item_type: str,
            qty: int = 1,
            net_price: Union[Decimal, None] = None,
            tax_rate: Union[Decimal, None] = ZERO,
            price: Union[Decimal, None] = None,
            decimal_places: int = 2,
            obj: object = None,
    ):
        """
        :param name: Name of the item, as it will appear on invoice.
        :param item_type: Custom defined item type or category, such as 'food', 'general' or 'discount'.
        :param qty: Item quantity, default is 1.
        :param net_price: Net price of the single item.
        :param tax_rate: Tax rate for the item.
        :param price: (Gross) price for the single item.
        :param decimal_places: Number of decimal places which will Decimal type use. Default is 2.
        :param obj: Arbitrary optional custom object attached to invoice item.
        """

        self.name = name
        self.item_type = item_type
        self.qty = qty
        self.tax_rate = tax_rate
        self.decimal_places = decimal_places
        self.obj = obj

        if price is not None:
            self.set_price(price)
        if net_price is not None:
            self.set_net_price(net_price)

    #----------------------------------------------------------------------------------------------

    def set_net_price(self, value: Decimal):
        """Set net price and automatically calculate gross price"""
        self.net_price = quanitize(value, self.decimal_places)
        self.price, self.tax_amount = net_to_gross(value, self.tax_rate, decimal_places=self.decimal_places)

    #----------------------------------------------------------------------------------------------

    def set_price(self, value: Decimal):
        """Set gross price and automatically calculate net price"""
        self.price = quanitize(value, self.decimal_places)
        self.net_price, self.tax_amount = gross_to_net(value, self.tax_rate, decimal_places=self.decimal_places)

    #----------------------------------------------------------------------------------------------

    def __str__(self):
        """Stringify it for debugging purposes"""
        return "[{item_type}] {qty}x {name} {price} (tax {tax_rate}%: {net} + {tax})".format(
            item_type=self.item_type,
            qty=self.qty,
            name=self.name,
            price=self.get_sum(),
            tax_rate=self.tax_rate,
            net=self.get_net_sum(),
            tax=self.get_tax_sum(),
        )

    #----------------------------------------------------------------------------------------------

    def get_net_sum(self) -> Decimal:
        """Calculates net sum for this invoice item"""
        return quanitize(self.net_price * self.qty, decimal_places=self.decimal_places)

    #----------------------------------------------------------------------------------------------

    def get_sum(self) -> Decimal:
        """Calculates gross sum for this invoice item"""
        return quanitize(self.price * self.qty, decimal_places=self.decimal_places)

    #----------------------------------------------------------------------------------------------

    def get_tax_sum(self) -> Decimal:
        """Calculates tax sum for this invoice item"""
        return quanitize(self.tax_amount * self.qty, decimal_places=self.decimal_places)

    #----------------------------------------------------------------------------------------------

    def serialize(self, json_output: bool = False) -> Union[dict, str]:
        """Serialize object.

        :param json_output: If true, result is string in json format. Otherwise it's a dict.
        :return: json formatted string or dict.
        """
        res = {
            'item_type': self.item_type,
            'qty': self.qty,
            'name': self.name,
            'price': self.price,
            'net_price': self.net_price,
            'tax_rate': self.tax_rate,
            'sum': self.get_sum(),
            'net_sum': self.get_net_sum(),
            'tax_sum': self.get_tax_sum(),
        }

        if json_output:
            res = json.dumps(res, cls=CustomJsonEncoder)

        return res

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
        """Stringify it for debugging purposes"""
        res = [f"Invoice container for tax rate {self.tax_rate}"]
        res += [str(c) for c in self]
        return '\n'.join(res)

    #----------------------------------------------------------------------------------------------

    def append(self, item: InvoiceItem):
        super().append(item)

    #----------------------------------------------------------------------------------------------

    def get_net_sum(self):
        return sum([c.get_net_sum() for c in self])

    #----------------------------------------------------------------------------------------------

    def get_sum(self):
        return sum([c.get_sum() for c in self])

    #----------------------------------------------------------------------------------------------

    def get_tax_sum(self):
        return sum([c.get_tax_sum() for c in self])

    #----------------------------------------------------------------------------------------------

    def find_item(self, name: str, price: Decimal, item_type: str = None):
        for item in self:
            # take item_type in comparison only if not None
            if (
                    item.name == name and item.price == price and item_type is None
            ) or (
                    item.name == name and item.price == price and item.item_type == item_type
            ):
                return item
        return None

    #----------------------------------------------------------------------------------------------


#**************************************************************************************************


class Invoice:
    """Main invoice class"""
    containers: List[InvoiceItemContainer] = None
    decimal_places: int = 2

    #----------------------------------------------------------------------------------------------

    def __init__(self, decimal_places: int = 2):
        """Main invoice class.
        :param decimal_places: Defines number of decimal places Decimal object will be using.
        """
        self.containers = list()
        self.decimal_places = decimal_places

    #----------------------------------------------------------------------------------------------

    def __str__(self):
        """Stringify it for debugging purposes"""
        res = [str(c) for c in self.containers]

        res.extend([
            '----------------',
            f"Amount      : {self.get_sum():>10}",
            f"Net price  : {self.get_net_sum():>10}",
            f"Tax price  : {self.get_tax_sum():>10}",
        ])

        return '\n'.join(res)

    #----------------------------------------------------------------------------------------------

    def add(self, item: InvoiceItem):
        """
        Adds InvoiceItem object to the invoice. Item will be automatically placed in tax category
        where it belongs. If item with same name, type and price already exists, just the
        quantity will be increased.

        :param item: Item to add
        """
        for container in self.containers:
            if container.tax_rate == item.tax_rate:
                existing_item = container.find_item(
                    name=item.name,
                    price=item.price,
                    item_type=item.item_type,
                )
                if existing_item is not None:
                    if existing_item.price == item.price:
                        existing_item.qty += item.qty
                    else:
                        existing_item.price += item.price * item.qty
                else:
                    container.append(item)
                return

        container = InvoiceItemContainer(tax_rate=item.tax_rate)
        self.containers.append(container)
        container.append(item)

    #----------------------------------------------------------------------------------------------

    def get_sum(self, item_type: str = None) -> Decimal:
        """Returns gross sum of all items, or items of declared type"""
        return sum([c.get_sum() for c in self.get_all_items(item_type=item_type)])

    #----------------------------------------------------------------------------------------------

    def get_net_sum(self, item_type: str = None) -> Decimal:
        """Returns net sum of all items, or items of declared type"""
        return sum([c.get_net_sum() for c in self.get_all_items(item_type=item_type)])

    #----------------------------------------------------------------------------------------------

    def get_tax_sum(self, item_type: str = None) -> Decimal:
        """Returns tax sum of all items, or items of declared type"""
        return sum([c.get_tax_sum() for c in self.get_all_items(item_type=item_type)])

    #----------------------------------------------------------------------------------------------

    def get_all_items(self, item_type: Union[str, List] = None) -> List[InvoiceItem]:
        """Returns all items or items of declared type"""
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

    def get_items_count(self, item_type: str = None) -> int:
        """Returns sum of all quantities for all items or items of declared type"""
        return sum(item.qty for item in self.get_all_items(item_type=item_type))

    #----------------------------------------------------------------------------------------------

    def group_by_tax_rate(self, item_type: str = None) -> list:
        """Returns structure of all items grouped by tax rate or items of declared type"""
        tax_rates = OrderedDict()

        for item in self.get_all_items(item_type=item_type):
            if item.tax_rate in tax_rates:
                d = tax_rates[item.tax_rate]
            else:
                d = {
                    'tax_rate': item.tax_rate,
                    'items': list(),
                    'price': ZERO,
                    'net': ZERO,
                    'tax': ZERO,
                }
                tax_rates.update({
                    item.tax_rate: d,
                })

            d['items'].append(item.serialize())
            d['price'] += item.get_sum()
            d['net'] += item.get_net_sum()
            d['tax'] += item.get_tax_sum()

        return list(tax_rates.values())

    #----------------------------------------------------------------------------------------------

    def serialize(self, item_type: str = None, json_output: bool = False) -> Union[dict, str]:
        """Serialize object.

        :param json_output: If true, result is string in json format. Otherwise it's a dict.
        :return: json formatted string or dict.
        """
        items = self.get_all_items(item_type=item_type)

        res = {
            'items': [item.serialize() for item in items],
            'total': {
                'price': sum(item.get_sum() for item in items),
                'net': sum(item.get_net_sum() for item in items),
                'tax': sum(item.get_tax_sum() for item in items),
            },
        }

        if json_output:
            res = json.dumps(res, cls=CustomJsonEncoder)

        return res

    #----------------------------------------------------------------------------------------------


#**************************************************************************************************
