# infoicer
Infoicer is a simple invoice items handler. It can group items by type and tax rate which helps in building the invoice for a customer.

## Features

- All price handling is utilized with `Decimal` type to avoid float rounding problems
- Easy to group invoice items by type and tax rate
- Implemented object serialization
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

print(invoice.serialize(json_output=True))
```

output:

```json
{
   "items":[
      {
         "item_type":"food",
         "qty":1,
         "name":"Ham",
         "price":10.0,
         "net_price":9.52,
         "tax_rate":5.0,
         "sum":10.0,
         "net_sum":9.52,
         "tax_sum":0.48
      },
      {
         "item_type":"food",
         "qty":3,
         "name":"Spam",
         "price":15.0,
         "net_price":14.29,
         "tax_rate":5.0,
         "sum":45.0,
         "net_sum":42.87,
         "tax_sum":2.13
      }
   ],
   "total":{
      "price":55.0,
      "net":52.39,
      "tax":2.61
   }
}
```

## Full demo

Check included [demo.py](https://github.com/edkirin/infoicer/blob/master/demo.py) for some more uses and features.

```
$ python demo.py

** Complete invoice
Product                         Tax rate %       Price     Qty         Sum
--------------------------------------------------------------------------
Cheese                                   5       69.97       2      139.94
Ham                                      5       26.07       2       52.14
Spam                                     5       11.54       5       57.70
Egg                                      5       31.95       1       31.95
Discount on food                         5      -10.00       1      -10.00
Mop                                     15      176.24       2      352.48
Vacuum cleaner                          15       97.26       2      194.52
Broom                                   15       98.92       4      395.68
--------------------------------------------------------------------------
Total sum                                                          1214.41
Total tax                                                           135.88
Tax rate                                 5                           12.94
Tax rate                                15                          122.94

** Invoice with food items only
Product                         Tax rate %       Price     Qty         Sum
--------------------------------------------------------------------------
Cheese                                   5       69.97       2      139.94
Ham                                      5       26.07       2       52.14
Spam                                     5       11.54       5       57.70
Egg                                      5       31.95       1       31.95
--------------------------------------------------------------------------
Total sum                                                           281.73
Total tax                                                            13.42
Tax rate                                 5                           13.42
```

## Licence

The code is available under MIT Licence.