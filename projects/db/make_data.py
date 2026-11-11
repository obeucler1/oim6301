"""Writes one CSV file per table for the Babson Bean Cafe database.

Run it with: uv run python projects/db/make_data.py
It always writes the same files, because `random.seed(42)` fixes the
random choices made below.
"""

import datetime
import random
from pathlib import Path

import polars as pl
from faker import Faker

random.seed(42)
fake = Faker()
Faker.seed(42)

data_dir = Path(__file__).parent / "data"
data_dir.mkdir(exist_ok=True)

# The 12 months of data end on this date. Part B of the project uses it too.
as_of = datetime.date(2026, 12, 5)
year_start = as_of - datetime.timedelta(days=365)

NUM_MEMBERS = 50
NUM_PRODUCTS = 24
NUM_OPTIONS = 10
NUM_ORDERS = 1200

# ---------------------------------------------------------------------
# members
# ---------------------------------------------------------------------
members_rows = []
for member_id in range(1, NUM_MEMBERS + 1):
    first_name = fake.first_name()
    mobile_number = fake.numerify("617-555-####")
    # about 15% of members never gave an email, so that column has to be optional
    has_email = random.random() < 0.85
    email = f"{first_name.lower()}{member_id}@example.com" if has_email else None
    days_before_as_of = random.randint(0, 365 * 3)
    join_date = as_of - datetime.timedelta(days=days_before_as_of)
    points_balance = random.randint(0, 500)
    members_rows.append(
        {
            "member_id": member_id,
            "first_name": first_name,
            "mobile_number": mobile_number,
            "email": email,
            "join_date": join_date,
            "points_balance": points_balance,
        }
    )

# ---------------------------------------------------------------------
# products
# ---------------------------------------------------------------------
# (name, category, cost range in cents, markup range)
product_catalog = [
    ("Drip Coffee", "coffee", (90, 130), (1.8, 2.4)),
    ("Americano", "coffee", (90, 130), (1.8, 2.4)),
    ("Latte", "coffee", (130, 170), (1.9, 2.6)),
    ("Cappuccino", "coffee", (130, 170), (1.9, 2.6)),
    ("Cortado", "coffee", (130, 170), (1.9, 2.6)),
    ("Mocha", "coffee", (150, 190), (1.9, 2.6)),
    ("Espresso Shot", "coffee", (60, 90), (2.0, 2.8)),
    ("Cold Brew", "coffee", (120, 160), (1.8, 2.4)),
    ("Iced Latte", "coffee", (140, 180), (1.9, 2.6)),
    ("Green Tea", "tea", (60, 90), (2.2, 3.0)),
    ("Black Tea", "tea", (60, 90), (2.2, 3.0)),
    ("Chai Latte", "tea", (120, 160), (1.9, 2.5)),
    ("Matcha Latte", "tea", (160, 200), (1.9, 2.5)),
    ("Herbal Tea", "tea", (60, 90), (2.2, 3.0)),
    ("Croissant", "food", (140, 180), (1.6, 2.1)),
    ("Blueberry Muffin", "food", (120, 160), (1.6, 2.1)),
    ("Bagel with Cream Cheese", "food", (130, 170), (1.6, 2.1)),
    ("Avocado Toast", "food", (250, 320), (1.5, 1.9)),
    ("Granola Yogurt Cup", "food", (200, 260), (1.5, 1.9)),
    ("Breakfast Sandwich", "food", (280, 340), (1.5, 1.9)),
    ("Chocolate Chip Cookie", "food", (90, 120), (1.8, 2.3)),
    ("Bottled Water", "other", (40, 60), (2.0, 2.6)),
    ("Babson Bean Mug", "other", (400, 600), (1.5, 1.8)),
    ("Bag of Whole Bean Coffee", "other", (600, 800), (1.6, 1.9)),
]

products_rows = []
for product_id, (name, category, cost_range, markup_range) in enumerate(
    product_catalog[:NUM_PRODUCTS], start=1
):
    cost_cents = random.randint(cost_range[0], cost_range[1])
    markup = random.uniform(markup_range[0], markup_range[1])
    price_cents = round(cost_cents * markup)
    is_available = random.random() < 0.9
    products_rows.append(
        {
            "product_id": product_id,
            "name": name,
            "category": category,
            "price": price_cents / 100,
            "cost": cost_cents / 100,
            "is_available": is_available,
        }
    )
# These two products are on the menu but nobody has ordered them yet,
# so order_lines never references them on purpose.
unused_product_ids = [products_rows[-1]["product_id"], products_rows[-2]["product_id"]]

# ---------------------------------------------------------------------
# options
# ---------------------------------------------------------------------
option_catalog = [
    ("Oat Milk", (20, 30), (50, 70)),
    ("Almond Milk", (20, 30), (50, 70)),
    ("Whole Milk", (0, 0), (0, 0)),
    ("Extra Shot", (25, 35), (75, 100)),
    ("Whipped Cream", (10, 15), (50, 60)),
    ("Vanilla Syrup", (10, 15), (50, 60)),
    ("Caramel Syrup", (10, 15), (50, 60)),
    ("Hazelnut Syrup", (10, 15), (50, 60)),
    ("Extra Sweetener", (0, 0), (0, 0)),
    ("Cinnamon Powder", (0, 0), (0, 0)),
]

options_rows = []
for option_id, (name, cost_range, price_range) in enumerate(
    option_catalog[:NUM_OPTIONS], start=1
):
    cost_cents = random.randint(cost_range[0], cost_range[1])
    price_cents = random.randint(price_range[0], price_range[1])
    options_rows.append(
        {
            "option_id": option_id,
            "name": name,
            "price": price_cents / 100,
            "cost": cost_cents / 100,
        }
    )
# This option is on the menu but has never been added to an order on purpose.
unused_option_id = options_rows[-1]["option_id"]

# ---------------------------------------------------------------------
# orders
# ---------------------------------------------------------------------
member_ids = [row["member_id"] for row in members_rows]
# the last 3 members joined but have never placed an order, on purpose
quiet_member_ids = member_ids[-3:]
orderable_member_ids = member_ids[:-3]
available_product_ids = [
    row["product_id"] for row in products_rows if row["product_id"] not in unused_product_ids
]
usable_option_ids = [
    row["option_id"] for row in options_rows if row["option_id"] != unused_option_id
]

orders_rows = []
# a cafe gets a morning rush and a smaller lunch bump, not flat traffic all day
open_hours = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
hour_weights = [2, 10, 14, 10, 6, 6, 9, 7, 5, 4, 4, 5, 3, 2]
for order_id in range(1, NUM_ORDERS + 1):
    days_after_start = random.randint(0, 365)
    order_date = year_start + datetime.timedelta(days=days_after_start)
    order_hour = random.choices(open_hours, weights=hour_weights)[0]
    order_time = datetime.time(
        hour=order_hour, minute=random.randint(0, 59), second=random.randint(0, 59)
    )
    ordered_at = datetime.datetime.combine(order_date, order_time)
    # about 55% of orders are placed by a loyalty member, the rest are walk-ins
    is_member_order = random.random() < 0.55
    member_id = random.choice(orderable_member_ids) if is_member_order else None
    channel = random.choices(["counter", "app"], weights=[0.65, 0.35])[0]
    orders_rows.append(
        {
            "order_id": order_id,
            "ordered_at": ordered_at,
            "member_id": member_id,
            "channel": channel,
        }
    )

# ---------------------------------------------------------------------
# order_lines and line_options, built together so each line's total is known
# ---------------------------------------------------------------------
products_by_id = {row["product_id"]: row for row in products_rows}
options_by_id = {row["option_id"]: row for row in options_rows}

order_lines_rows = []
line_options_rows = []
order_totals_cents = {}  # order_id -> total price owed, in cents
line_id = 1
for order in orders_rows:
    order_id = order["order_id"]
    num_lines = random.randint(1, 4)
    chosen_products = random.sample(available_product_ids, min(num_lines, len(available_product_ids)))
    order_total_cents = 0
    for product_id in chosen_products:
        product = products_by_id[product_id]
        quantity = random.randint(1, 3)
        price_charged_cents = round(product["price"] * 100)
        order_lines_rows.append(
            {
                "line_id": line_id,
                "order_id": order_id,
                "product_id": product_id,
                "quantity": quantity,
                "price_charged": price_charged_cents / 100,
            }
        )
        order_total_cents += quantity * price_charged_cents

        # 0 to 2 options on this line, no option repeated on the same line
        num_options = random.choices([0, 1, 2], weights=[0.5, 0.35, 0.15])[0]
        chosen_options = random.sample(usable_option_ids, min(num_options, len(usable_option_ids)))
        for option_id in chosen_options:
            option = options_by_id[option_id]
            option_price_cents = round(option["price"] * 100)
            line_options_rows.append(
                {
                    "line_id": line_id,
                    "option_id": option_id,
                    "price_charged": option_price_cents / 100,
                }
            )
            # an option is charged once per unit on the line
            order_total_cents += option_price_cents * quantity

        line_id += 1

    order_totals_cents[order_id] = order_total_cents

# ---------------------------------------------------------------------
# payments
# ---------------------------------------------------------------------
# These two orders break the rule "an order's payments add up to its total"
# on purpose. A CHECK constraint cannot hold this rule, because it compares
# orders, order_lines, line_options and payments together, so these two rows
# are not refused: section 2 of build.py writes down their order_ids.
broken_order_ids = random.sample(list(order_totals_cents.keys()), 2)

payment_methods = ["cash", "card", "app", "points"]
payments_rows = []
payment_id = 1
for order_id, total_cents in order_totals_cents.items():
    if order_id == broken_order_ids[0]:
        # paid less than the order came to
        paid_cents = max(1, total_cents - random.randint(200, 500))
    elif order_id == broken_order_ids[1]:
        # paid more than the order came to
        paid_cents = total_cents + random.randint(200, 500)
    else:
        paid_cents = total_cents

    num_payments = random.choices([1, 2], weights=[0.8, 0.2])[0]
    if num_payments == 1 or paid_cents < 2:
        splits = [paid_cents]
    else:
        first_cents = random.randint(1, paid_cents - 1)
        splits = [first_cents, paid_cents - first_cents]

    for amount_cents in splits:
        method = random.choice(payment_methods)
        payments_rows.append(
            {
                "payment_id": payment_id,
                "order_id": order_id,
                "method": method,
                "amount": amount_cents / 100,
            }
        )
        payment_id += 1

print("Rows with nothing attached:")
print(f"  products never ordered: {unused_product_ids}")
print(f"  option never used on a line: {unused_option_id}")
print(f"  members who never placed an order: {quiet_member_ids}")
print()
print("Rows that break a rule on purpose (payments do not add up to the order total):")
print(f"  order_id {broken_order_ids[0]}: paid less than the order's total")
print(f"  order_id {broken_order_ids[1]}: paid more than the order's total")

# ---------------------------------------------------------------------
# write the CSV files
# ---------------------------------------------------------------------
pl.DataFrame(members_rows).write_csv(data_dir / "members.csv")
pl.DataFrame(products_rows).write_csv(data_dir / "products.csv")
pl.DataFrame(options_rows).write_csv(data_dir / "options.csv")
pl.DataFrame(orders_rows).write_csv(data_dir / "orders.csv")
pl.DataFrame(order_lines_rows).write_csv(data_dir / "order_lines.csv")
pl.DataFrame(line_options_rows).write_csv(data_dir / "line_options.csv")
pl.DataFrame(payments_rows).write_csv(data_dir / "payments.csv")

print()
print("Row counts:")
print(f"  members: {len(members_rows)}")
print(f"  products: {len(products_rows)}")
print(f"  options: {len(options_rows)}")
print(f"  orders: {len(orders_rows)}")
print(f"  order_lines: {len(order_lines_rows)}")
print(f"  line_options: {len(line_options_rows)}")
print(f"  payments: {len(payments_rows)}")
