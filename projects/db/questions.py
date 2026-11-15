import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import datetime

    return datetime, duckdb, mo


@app.cell
def _(duckdb, mo):
    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return


@app.cell
def _(datetime):
    # every question below counts "last 30 days" and "last month" back from this date
    as_of = datetime.date(2026, 12, 5)
    as_of
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 3. Reading It Back

    My question: Every order's payments checked against its total, and a list of the orders where they do not match. (three tables or more) (checks a rule) It needs order_lines, line_options and payments.

    **My prediction**

    To check a payment against an order's total, the query has to rebuild that total from order_lines left joined with line_options on line_id (a line with no options shows up once, a line with options shows up once per option). Then it joins that to payments on order_id, before it GROUPS BY. A single order can have more than one payment such as being paid with half cash and half card, so this join can multiply rows again.

    I already know from part A, that order_lines left joined with line_options is about 3,369 rows. I also know payments has 1,446 rows and 1,200 orders, which is about 1.2 payments per order.

    If we joined payments on order_id it would turn each of those 3,369 rows into about 1.2 rows, which is the average number of payments an order has. So I predict about 3,369 × 1.2 = 4,040 rows before grouping.
    """)
    return


if __name__ == "__main__":
    app.run()
