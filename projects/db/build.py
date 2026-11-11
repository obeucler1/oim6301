import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import polars as pl
    import altair as alt

    return alt, duckdb, mo, pl


@app.cell
def _(duckdb, mo):
    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return ask, database


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #1. The Tables.
    One CREATE TABLE for each table in your ERD, with every primary key and foreign key declared, and with NOT NULL, CHECK, UNIQUE and DEFAULT where the scenario's rules call for them. Chapter D of the SQL handbook, §24, has the syntax.
    """)
    return


@app.cell
def _(database, duckdb, mo):
    database.unlink(missing_ok=True)
    _data_dir = mo.notebook_dir() / "data"

    with duckdb.connect(database) as _con:
        _con.execute("""
        CREATE TABLE members (
            member_id INTEGER PRIMARY KEY,
            first_name VARCHAR NOT NULL,
            mobile_number VARCHAR NOT NULL,
            email VARCHAR,
            join_date DATE NOT NULL,
            points_balance INTEGER NOT NULL DEFAULT 0 CHECK (points_balance >= 0)
        );

        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            category VARCHAR NOT NULL CHECK (category IN ('coffee', 'tea', 'food', 'other')),
            price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
            cost DECIMAL(10,2) NOT NULL CHECK (cost >= 0),
            is_available BOOLEAN NOT NULL DEFAULT TRUE,
            CHECK (price >= cost)
        );

        CREATE TABLE options (
            option_id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
            cost DECIMAL(10,2) NOT NULL CHECK (cost >= 0)
        );

        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            ordered_at TIMESTAMP NOT NULL,
            member_id INTEGER REFERENCES members(member_id),
            channel VARCHAR NOT NULL CHECK (channel IN ('counter', 'app'))
        );

        CREATE TABLE order_lines (
            line_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL REFERENCES orders(order_id),
            product_id INTEGER NOT NULL REFERENCES products(product_id),
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            price_charged DECIMAL(10,2) NOT NULL CHECK (price_charged >= 0)
        );

        CREATE TABLE line_options (
            line_id INTEGER NOT NULL REFERENCES order_lines(line_id),
            option_id INTEGER NOT NULL REFERENCES options(option_id),
            price_charged DECIMAL(10,2) NOT NULL CHECK (price_charged >= 0),
            PRIMARY KEY (line_id, option_id)
        );

        CREATE TABLE payments (
            payment_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL REFERENCES orders(order_id),
            method VARCHAR NOT NULL CHECK (method IN ('cash', 'card', 'app', 'points')),
            amount DECIMAL(10,2) NOT NULL CHECK (amount > 0)
        );
        """)

        # load in an order that respects every foreign key: the table a key
        # points to has to be filled before the table that references it
        _con.execute(f"INSERT INTO members SELECT * FROM read_csv('{_data_dir}/members.csv')")
        _con.execute(f"INSERT INTO products SELECT * FROM read_csv('{_data_dir}/products.csv')")
        _con.execute(f"INSERT INTO options SELECT * FROM read_csv('{_data_dir}/options.csv')")
        _con.execute(f"INSERT INTO orders SELECT * FROM read_csv('{_data_dir}/orders.csv')")
        _con.execute(
            f"INSERT INTO order_lines SELECT * FROM read_csv('{_data_dir}/order_lines.csv')"
        )
        _con.execute(
            f"INSERT INTO line_options SELECT * FROM read_csv('{_data_dir}/line_options.csv')"
        )
        _con.execute(f"INSERT INTO payments SELECT * FROM read_csv('{_data_dir}/payments.csv')")

        # the question staff would ask every week: what to restock and feature
        _con.execute("""
            CREATE VIEW top_selling_products AS
                SELECT p.product_id, p.name, p.category,
                       SUM(ol.quantity) AS units_sold,
                       SUM(ol.quantity * ol.price_charged) AS revenue
                FROM products p
                JOIN order_lines ol ON ol.product_id = p.product_id
                GROUP BY p.product_id, p.name, p.category
        """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #2 The Data.
    Ask your agent for a script, projects/db/make_data.py, that writes data for every table as CSV files in projects/db/data/, and load them. The data has to obey every rule, with one exception: for each question marked (checks a rule) on your list, break its rule on purpose in exactly two rows, and write down which two in this section. If your tables make the database refuse those rows, your design holds that rule with a constraint: say so here, and show the refusal in that question's answer instead. It has to cover the 12 months up to a date you choose, your as_of date, which Part B uses. You can start from this prompt. Replace each part in angle brackets, brackets included, with your own text:

    Here are the CREATE TABLE statements for my database: <your CREATE TABLE statements>.
    Write a Python script, projects/db/make_data.py, that writes one CSV file
    per table into projects/db/data/.
    - Follow every rule of my scenario: <your scenario's rules>.
    - Break these rules on purpose, each in exactly two rows, and print which rows:
      <the rules your checking questions are about>.
    - Make <your scenario's amounts of data>, covering the 12 months up to <your as_of date>.
    - Include on purpose some rows with nothing attached, such as <one from your scenario>.
    - Use a fixed random seed, so that the script writes the same files every time.

    Your scenario says how much data it needs; for your own domain, at least 10 rows in each table that lists things the business keeps and 1,000 rows across the tables that record what happens. Include on purpose some rows with nothing attached, so that the questions about them have an answer. Read the data before you keep it, because an agent's first try usually breaks a rule nobody wrote down: a task assigned before somebody started, a sale of shares nobody held, two appointments at once, a price nobody would charge.

    (Info for this section: The rules it works by

    - A quantity is more than zero, and so is a payment.
    - On the menu, a product's price is never below its cost.
    - An order line belongs to exactly one order and one product, and an option on a line belongs to exactly one line.
    - An option appears at most once on a line, and it is charged once for every unit on the line: two lattes with oat milk pay for oat milk twice.
    - A payment's method is one of the four listed above.
    - An order's payments add up to the order's total, its lines and their options together. A CHECK cannot hold a rule that spans tables, so this one is checked with a query.

    The data you need: at least 40 members, 20 products, eight options and 1,000 orders.)

    **Which rows break a rule on purpose.**

    - *A product's price is never below its cost.* One table can hold this with a single `CHECK (price >= cost)`, so I added that constraint to `products` instead of writing bad rows into `products.csv`. `make_data.py` never writes a product priced below its cost, so the database holds this rule and refuses it; section 5 shows the refusal.
    - *An order's payments add up to the order's total.* This rule spans `orders`, `order_lines`, `line_options` and `payments`, so a `CHECK` cannot hold it. `make_data.py` deliberately makes exactly two orders' payments not match their total: one order paid less than it owed, one paid more. The seed is fixed, so the same two `order_id`s come back every run; the cell below finds them with the query described above.

    **Rows with nothing attached**, also on purpose: 2 products nobody has ordered, 1 option never added to a line, and 3 members who joined but never placed an order.
    """)
    return


@app.cell
def _(ask):
    ask("""
        WITH line_totals AS (
            SELECT order_id, SUM(quantity * price_charged) AS lines_total
            FROM order_lines
            GROUP BY order_id
        ),
        option_totals AS (
            SELECT ol.order_id, SUM(lo.price_charged * ol.quantity) AS options_total
            FROM line_options lo
            JOIN order_lines ol ON ol.line_id = lo.line_id
            GROUP BY ol.order_id
        ),
        order_totals AS (
            SELECT lt.order_id, lt.lines_total + COALESCE(ot.options_total, 0) AS order_total
            FROM line_totals lt
            LEFT JOIN option_totals ot ON ot.order_id = lt.order_id
        ),
        paid AS (
            SELECT order_id, SUM(amount) AS paid_total
            FROM payments
            GROUP BY order_id
        )
        SELECT ot.order_id, ot.order_total, p.paid_total
        FROM order_totals ot
        JOIN paid p ON p.order_id = ot.order_id
        WHERE round(ot.order_total, 2) != round(p.paid_total, 2)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #3 A Look at the Data.
    Read one of your CSV files with polars and chart one column whose shape you can judge, such as appointments by day of the week, orders by hour, or one asset's closing prices. Write one sentence on whether a real business would look like that, and if it would not, what you changed in make_data.py.
    """)
    return


@app.cell
def _(alt, mo, pl):
    _orders = pl.read_csv(mo.notebook_dir() / "data" / "orders.csv", try_parse_dates=True)
    _by_hour = (
        _orders.with_columns(pl.col("ordered_at").dt.hour().alias("hour"))
        .group_by("hour")
        .agg(pl.len().alias("orders"))
        .sort("hour")
    )
    orders_by_hour_chart = mo.ui.altair_chart(
        _by_hour.plot.bar(
            x=alt.X("hour", title="Hour of day"),
            y=alt.Y("orders", title="Orders"),
        ).properties(title="Orders by hour of day")
    )
    orders_by_hour_chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This matches a real cafe: orders climb into a morning rush around 7-9am, dip mid-morning, and get a smaller bump at lunch, instead of being spread flat across every hour; I weighted `random.choices` in `make_data.py` toward those hours so the order times aren't drawn uniformly across the day.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #4. Row Counts.
    Every table with its number of rows.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT 'members' AS table_name, count(*) AS rows FROM members
        UNION ALL SELECT 'products', count(*) FROM products
        UNION ALL SELECT 'options', count(*) FROM options
        UNION ALL SELECT 'orders', count(*) FROM orders
        UNION ALL SELECT 'order_lines', count(*) FROM order_lines
        UNION ALL SELECT 'line_options', count(*) FROM line_options
        UNION ALL SELECT 'payments', count(*) FROM payments
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #5. A Row It Refuses.
    Insert one row that breaks one of your rules, and show the message the database gives back. ask() only reads, so open a short write connection of its own for the insert, with duckdb.connect(database) as _con:, the way notebook 6 does, and put it inside try and except, so that the rest of the notebook still runs.

    A coffee that costs the shop $5.00 but is sold for $1.00: the `CHECK (price >= cost)` constraint on `products` holds the rule "a product's price is never below its cost", so the database refuses it.
    """)
    return


@app.cell
def _(database, duckdb):
    try:
        with duckdb.connect(database) as _con:
            _con.execute(
                "INSERT INTO products VALUES (9001, 'Priced Below Cost', 'coffee', 1.00, 5.00, true)"
            )
        refused = "accepted"
    except duckdb.ConstraintException as _error:
        refused = str(_error).splitlines()[0]
    refused
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #6. Answers You Already Knew.
    Three queries whose answers you knew before you ran them, because you know what you asked your agent for, with the answer you expected written next to each.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Expected: 50, because `make_data.py` sets `NUM_MEMBERS = 50`.
    """)
    return


@app.cell
def _(ask):
    ask("SELECT count(*) AS members FROM members")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Expected: 9, the coffee drinks I listed in `product_catalog`.
    """)
    return


@app.cell
def _(ask):
    ask("SELECT count(*) AS coffee_products FROM products WHERE category = 'coffee'")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Expected: 2, the two products `make_data.py` keeps out of `order_lines` on purpose.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT count(*) AS products_never_ordered
        FROM products
        WHERE product_id NOT IN (SELECT product_id FROM order_lines)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #7. A View.
    One question the business would ask every week, saved with CREATE VIEW in the cell that builds the database, so that anybody can ask for it by name and always get the current rows. Notebook 6 covers views in section 5, after GROUP BY. At least one of your answers in Part B must use it. Chapter D of the SQL handbook, §28.

    Every week, Babson Bean asks what to restock and feature: the view `top_selling_products`, built in the cell for section 1, adds up each product's units sold and revenue from `order_lines`. Asking for it by name always runs that query again on the current rows.
    """)
    return


@app.cell
def _(ask):
    ask("SELECT * FROM top_selling_products ORDER BY revenue DESC LIMIT 5")
    return


if __name__ == "__main__":
    app.run()
