from src.infoicer import Invoice, InvoiceItem

import random
from decimal import Decimal


# define some products for demo
FOOD_ITEMS = [
    "Cheese", "Ham", "Spam", "Egg",
]
FOOD_TAX_RATE = Decimal(5)

HOUSEHOLD_ITEMS = [
    "Mop", "Vacuum cleaner", "Broom",
]
HOUSEHOLD_TAX_RATE = Decimal(15)

# create invoice object
invoice = Invoice()

# create food items
for item in FOOD_ITEMS:
    invoice.add(InvoiceItem(
        name=item,
        item_type='food',
        price=Decimal(random.random() * 100),
        qty=random.randint(1, 5),
        tax_rate=FOOD_TAX_RATE,
    ))

# create household items
for item in HOUSEHOLD_ITEMS:
    invoice.add(InvoiceItem(
        name=item,
        item_type='household',
        price=Decimal(random.random() * 200),
        qty=random.randint(1, 5),
        tax_rate=HOUSEHOLD_TAX_RATE,
    ))

# set discount on food items
invoice.add(InvoiceItem(
    name=f"Discount on food",
    item_type='discount',
    price=Decimal(-10),
    tax_rate=FOOD_TAX_RATE,
))


def print_invoice(invoice: Invoice, item_type: str = None):
    header = f"{'Product':<30}{'Tax rate %':>12}{'Price':>12}{'Qty':>8}{'Sum':>12}"
    print(header)
    print('-' * len(header))

    for item in invoice.get_all_items(item_type=item_type):
        print(f"{item.name:<30}{item.tax_rate:>12}{item.price:>12}{item.qty:>8}{item.get_sum():>12}")

    print('-' * len(header))

    amount_sum = invoice.get_amount_sum(item_type=item_type)
    tax_sum = invoice.get_tax_sum(item_type=item_type)

    print(f"{'Total sum':<30}{amount_sum:>44}")
    print(f"{'Total tax':<30}{tax_sum:>44}")

    for item in invoice.group_by_tax_rate(item_type=item_type):
        print(f"{'Tax rate':<30}{item['tax_rate']:>12}{item['tax']:>32}")

    print()


print("** Complete invoice")
print_invoice(invoice)

# print("** Invoice with food items only")
# print_invoice(invoice, item_type='food')
#
# print("** Serialized invoice as json")
# print(invoice.serialize(json_output=True))
