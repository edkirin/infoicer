# infoicer
Infoicer is a simple invoice items handler. It can group items by type and tax rate which helps in building the invoice for a customer.

## Features

- All price handling is utilized with `Decimal` type to avoid float rounding problems
- Easy to group invoice items by type and tax rate
- Already implemented object serialization
- No external dependencies

## Installation

From PyPi:

```bash
$ pip install infoicer
```

or clone repository:

```bash
$ git clone git@github.com:edkirin/infoicer.git
```

## Basic usage

```python
from infoicer import Invoice, InvoiceItem
from decimal import Decimal

invoice = Invoice()

invoice.add(InvoiceItem(
    name="Ham",
    item_type='food',
    price=Decimal(10),
    qty=1,
    tax_rate=Decimal(5),
))

invoice.add(InvoiceItem(
    name="Spam",
    item_type='food',
    price=Decimal(15),
    qty=3,
    tax_rate=Decimal(5),
))
```

Check included [demo.py](https://github.com/edkirin/infoicer/blob/master/demo.py).

## Licence

The code is available under MIT Licence.