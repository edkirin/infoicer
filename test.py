from src.infoicer import Invoice, InvoiceItem

import random
from decimal import Decimal


invoice = Invoice()

for c in range(5):
    invoice.add(InvoiceItem(
        name=f"item",
        item_type='burek',
        amount=Decimal(random.random() * 1000),
        tax_rate=Decimal(25),
    ))

for c in range(5):
    invoice.add(InvoiceItem(
        name=f"item {c}",
        item_type='jaje',
        amount=Decimal(random.random() * 1000),
        tax_rate=Decimal(25),
    ))

print(invoice)

print('-' * 20)

for c in invoice.get_all_items(item_type='jaje'):
    print(c.serialize())

print('-' * 20)


print(invoice.group_by_tax_rate())
