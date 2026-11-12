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

    return (ask,)


@app.cell
def _(datetime):
    # every question below counts "last 30 days" and "last month" back from this date
    as_of = datetime.date(2026, 12, 5)
    as_of
    return (as_of,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 3. Reading It Back

    ** *For each coffee and tea product, the average number of options on its lines, counting a line with no options as zero.* It needs 3 tables: `products`, `order_lines` and `line_options`.

    **My prediction**

    The query would join `products` (kept to `category IN ('coffee', 'tea')`) to `order_lines` on `product_id`, then `LEFT JOIN`s `line_options` on `line_id`, all before any `GROUP BY`. A `LEFT JOIN` keeps one row for an order line with no options, and one row per option for a line that has some, so each order line turns into `max(1, number of its options)` rows.

    I know from part A that:

    `order_lines` has 2,956 rows, `make_data.py` takes each line's product from the 22 products that ever get ordered, and both of those 2 unused products are in the `other` category, they arent `coffee` or `tea`. So all 9 coffee and 5 tea products show in `order_lines`, and that  `make_data.py` gives each line 0 options with probability 0.5, 1 option with probability 0.35, and 2 options with probability 0.15, so `max(1, options)` averages to `0.5(1) + 0.35(1) + 0.15(2) = 1.15` rows per line.

    This means that about `2,956 × 14/22 ≈ 1,881` of the order lines are for a coffee or tea, and the left join turns each of those into about 1.15 rows, so **I predict about `1,881 × 1.15 ≈ 2,163` rows before any grouping.**
    """)
    return


if __name__ == "__main__":
    app.run()
