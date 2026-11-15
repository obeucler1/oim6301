import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import datetime
    import polars as pl
    import altair as alt

    return alt, datetime, duckdb, mo


@app.cell
def _(duckdb, mo):
    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return (ask,)


@app.cell
def _(datetime):
    # the questions below are counting the "last 30 days" and "last month" back from this date
    as_of = datetime.date(2026, 12, 5)

    # "last month" is the last full calendar month before as_of: November 2026
    last_month_end = as_of.replace(day=1) - datetime.timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    # "last 60 days" is the 60 days before as_of (2026, 12,5)
    last_60_start = as_of - datetime.timedelta(days=59)

    # the day after last_month_end, so "< last_month_end_exclusive" covers the whole day of orders and things in last_month_end's day
    last_month_end_exclusive = last_month_end + datetime.timedelta(days=1)

    as_of
    return as_of, last_60_start, last_month_end_exclusive, last_month_start


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Babson Bean Cafe — Business Questions

    All ten questions below ask `database.duckdb` through the `ask()` function defined above, a copy of the one in `build.py`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The three best-selling products last month, by units
    """)
    return


@app.cell
def _(ask, last_month_end_exclusive, last_month_start):
    q1_top_products = ask(
        f"""
        SELECT p.product_id, p.name, SUM(ol.quantity) AS units
        FROM order_lines ol
        JOIN orders o ON o.order_id = ol.order_id
        JOIN products p ON p.product_id = ol.product_id
        WHERE o.ordered_at >= '{last_month_start}'
          AND o.ordered_at < '{last_month_end_exclusive}'
        GROUP BY p.product_id, p.name
        ORDER BY units DESC
        LIMIT 3
        """)
    q1_top_products
    return (q1_top_products,)


@app.cell
def _(q1_top_products):
    _names = q1_top_products["name"].to_list()
    _units = q1_top_products["units"].to_list()
    f"""The three best-selling products by units in last month were {_names[0]} with {_units[0]} units, {_names[1]} with {_units[1]} units, and {_names[2]} with {_units[2]} units."""
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Revenue, cost and margin by menu category

    This counts what each category's options got too, with every option counted under the category of the product on its line (ex: coffee with oat milk doesnt give oat milk a new category, it just gets added to coffee revenue).
    """)
    return


@app.cell
def _(ask):
    q2_category_margin = ask(
        """
        WITH line_rev AS (
            SELECT p.category,
                   SUM(ol.quantity * ol.price_charged) AS line_revenue,
                   SUM(ol.quantity * p.cost) AS line_cost
            FROM order_lines ol
            JOIN products p ON p.product_id = ol.product_id
            GROUP BY p.category
        ),
        option_rev AS (
            SELECT p.category,
                   SUM(ol.quantity * lo.price_charged) AS option_revenue,
                   SUM(ol.quantity * o.cost) AS option_cost
            FROM line_options lo
            JOIN order_lines ol ON ol.line_id = lo.line_id
            JOIN products p ON p.product_id = ol.product_id
            JOIN options o ON o.option_id = lo.option_id
            GROUP BY p.category
        )
        SELECT lr.category,
               lr.line_revenue + COALESCE(opr.option_revenue, 0) AS revenue,
               lr.line_cost + COALESCE(opr.option_cost, 0) AS cost,
               (lr.line_revenue + COALESCE(opr.option_revenue, 0))
                   - (lr.line_cost + COALESCE(opr.option_cost, 0)) AS margin
        FROM line_rev lr
        LEFT JOIN option_rev opr ON opr.category = lr.category
        ORDER BY margin DESC
        """)
    q2_category_margin
    return (q2_category_margin,)


@app.cell
def _(q2_category_margin):
    _best_category = None
    _best_margin = None
    for _row in q2_category_margin.iter_rows(named=True):
        if _best_margin is None or _row["margin"] > _best_margin:
            _best_margin = _row["margin"]
            _best_category = _row["category"]
            _best_revenue = _row["revenue"]

    f"""Coffee and tea options are already folded into their product's category, and {_best_category} makes the most profit, with a margin of ${_best_margin:,.2f} and ${_best_revenue:,.2f} of revenue."""
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Members' orders, total spent and average order, above the members' average

     For each member: the number of orders, the total spent and the average order, keeping only the members whose total spent is above that members average.
    """)
    return


@app.cell
def _(ask):
    q3_top_spenders = ask(
        """
        WITH order_totals AS (
            SELECT ol.order_id, SUM(ol.quantity * ol.price_charged) AS line_total
            FROM order_lines ol
            GROUP BY ol.order_id
        ),
        option_totals AS (
            SELECT ol.order_id, SUM(ol.quantity * lo.price_charged) AS option_total
            FROM line_options lo
            JOIN order_lines ol ON ol.line_id = lo.line_id
            GROUP BY ol.order_id
        ),
        full_totals AS (
            SELECT ot.order_id, ot.line_total + COALESCE(opt.option_total, 0) AS order_total
            FROM order_totals ot
            LEFT JOIN option_totals opt ON opt.order_id = ot.order_id
        ),
        member_orders AS (
            SELECT o.member_id,
                   COUNT(*) AS num_orders,
                   SUM(ft.order_total) AS total_spent,
                   AVG(ft.order_total) AS avg_order
            FROM orders o
            JOIN full_totals ft ON ft.order_id = o.order_id
            WHERE o.member_id IS NOT NULL
            GROUP BY o.member_id
        )
        SELECT m.member_id, m.first_name, mo.num_orders,
               ROUND(mo.total_spent, 2) AS total_spent,
               ROUND(mo.avg_order, 2) AS avg_order
        FROM member_orders mo
        JOIN members m ON m.member_id = mo.member_id
        WHERE mo.total_spent > (SELECT AVG(total_spent) FROM member_orders)
        ORDER BY mo.total_spent DESC
        """)
    q3_top_spenders
    return (q3_top_spenders,)


@app.cell
def _(ask, q3_top_spenders):
    _members_with_orders = ask(
        """
        SELECT COUNT(DISTINCT member_id) AS n
        FROM orders
        WHERE member_id IS NOT NULL
        """
    )["n"][0]
    _kept = q3_top_spenders.height

    f"""Of the {_members_with_orders} members who have ever ordered, {_kept} spend more than the members average order total (I interpreted "the members average" as the average total spent per member, not the average order size)."""
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Orders whose payments don't match their total

    Every order's payments checked against its total, and a list of the orders where they don't match.
    """)
    return


@app.cell
def _(ask):
    q4_mismatches = ask(
        """
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
        SELECT ot.order_id,
               ROUND(ot.order_total, 2) AS order_total,
               ROUND(p.paid_total, 2) AS paid_total
        FROM order_totals ot
        JOIN paid p ON p.order_id = ot.order_id
        WHERE round(ot.order_total, 2) != round(p.paid_total, 2)
        ORDER BY ot.order_id
        """)
    q4_mismatches
    return (q4_mismatches,)


@app.cell
def _(q4_mismatches):
    _rows = list(q4_mismatches.iter_rows(named=True))
    _parts = []
    for _r in _rows:
        _diff = _r["paid_total"] - _r["order_total"]
        _word = "overpaid" if _diff > 0 else "underpaid"
        _parts.append(
            f"order {_r['order_id']} was {_word} (${_r['paid_total']:.2f} paid vs. ${_r['order_total']:.2f} owed)"
        )

    f"""Two orders payments don't match their total: {_parts[0]} and {_parts[1]}. These are the two rows `make_data.py` intentionally broke in Part A."""
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The members who joined and have never ordered
    """)
    return


@app.cell
def _(ask):
    q5_never_ordered = ask(
        """
        SELECT m.member_id, m.first_name, m.join_date
        FROM members m
        LEFT JOIN orders o ON o.member_id = m.member_id
        WHERE o.order_id IS NULL
        ORDER BY m.member_id
        """)
    q5_never_ordered
    return (q5_never_ordered,)


@app.cell
def _(q5_never_ordered):
    _names = q5_never_ordered["first_name"].to_list()
    f"""{q5_never_ordered.height} members joined but have never placed an order: {", ".join(_names)}."""
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. The share of orders paid at least partly with points, for each month
    """)
    return


@app.cell
def _(ask):
    q6_points_share = ask(
        """
        WITH monthly_orders AS (
            SELECT date_trunc('month', ordered_at) AS month, COUNT(*) AS total_orders
            FROM orders
            GROUP BY month
        ),
        points_orders AS (
            SELECT date_trunc('month', o.ordered_at) AS month,
                   COUNT(DISTINCT o.order_id) AS points_orders
            FROM orders o
            JOIN payments p ON p.order_id = o.order_id
            WHERE p.method = 'points'
            GROUP BY month
        )
        SELECT mo.month, mo.total_orders, COALESCE(po.points_orders, 0) AS points_orders,
               ROUND(COALESCE(po.points_orders, 0)::DOUBLE / mo.total_orders, 3) AS points_share
        FROM monthly_orders mo
        LEFT JOIN points_orders po ON po.month = mo.month
        ORDER BY mo.month
        """)
    q6_points_share
    return (q6_points_share,)


@app.cell
def _(q6_points_share):
    _highest = None
    _lowest = None
    for _row in q6_points_share.iter_rows(named=True):
        if _highest is None or _row["points_share"] > _highest["points_share"]:
            _highest = _row
        if _lowest is None or _row["points_share"] < _lowest["points_share"]:
            _lowest = _row

    f"""Each month, about 1/4 to 1/3 of orders are paid at least with a few points, with a low of {_lowest['points_share']:.1%} in {_lowest['month'].strftime('%B %Y')} to a high of {_highest['points_share']:.1%} in {_highest['month'].strftime('%B %Y')}."""
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. The products, available or not, that have not sold in the last 60 days
    """)
    return


@app.cell
def _(as_of, ask, last_60_start):
    q7_not_sold_60d = ask(
        f"""
        SELECT p.product_id, p.name, p.category, p.is_available
        FROM products p
        WHERE p.product_id NOT IN (
            SELECT ol.product_id
            FROM order_lines ol
            JOIN orders o ON o.order_id = ol.order_id
            WHERE o.ordered_at >= '{last_60_start}' AND o.ordered_at <= '{as_of}'
        )
        ORDER BY p.product_id
        """)
    q7_not_sold_60d
    return (q7_not_sold_60d,)


@app.cell
def _(q7_not_sold_60d):
    _names = q7_not_sold_60d["name"].to_list()
    f"""In the last 60 days, {q7_not_sold_60d.height} products haven't sold: {" and ".join(_names)}. They are both are still available which means we have not taken them off the shelf, so it seems like customers just aren't buying these products anymore."""
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Average number of options per line, for each coffee and tea product

    A line with no options counts as zero. This is the question I predicted for the Reading It Back section.
    """)
    return


@app.cell
def _(ask):
    q8_avg_options = ask(
        """
        SELECT p.product_id, p.name, p.category, ROUND(AVG(sub.opt_count), 3) AS avg_options
        FROM (
            SELECT ol.line_id, ol.product_id, COUNT(lo.option_id) AS opt_count
            FROM order_lines ol
            LEFT JOIN line_options lo ON lo.line_id = ol.line_id
            GROUP BY ol.line_id, ol.product_id
        ) sub
        JOIN products p ON p.product_id = sub.product_id
        WHERE p.category IN ('coffee', 'tea')
        GROUP BY p.product_id, p.name, p.category
        ORDER BY avg_options DESC
        """)
    q8_avg_options
    return (q8_avg_options,)


@app.cell
def _(q8_avg_options):
    _top = q8_avg_options.row(0, named=True)
    _bottom = q8_avg_options.row(q8_avg_options.height - 1, named=True)
    f"""From all {q8_avg_options.height} of the coffee and tea products, their lines average a little over 1/2 an option each, with the lowest at {_bottom['avg_options']} per line for {_bottom['name']} and highest being {_top['avg_options']} for {_top['name']}."""
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. (My own question) The 5 best-selling products overall, by their revenue.

    A manager needs to restock and plan the menu so they would want to know our overall best selling products, not just last month's.   This uses the top_selling_products in Question 7 from build.py.
    """)
    return


@app.cell
def _(ask):
    q9_top_sellers_view = ask(
        "SELECT * FROM top_selling_products ORDER BY revenue DESC LIMIT 5"
    )
    q9_top_sellers_view
    return (q9_top_sellers_view,)


@app.cell
def _(q9_top_sellers_view):
    _top = q9_top_sellers_view.row(0, named=True)
    _food_count = 0
    for _row in q9_top_sellers_view.iter_rows(named=True):
        if _row["category"] == "food":
            _food_count += 1

    f"""Using the top_selling_products view, the overall top revenue product is the {_top['name']} at ${_top['revenue']:,.2f}, and {_food_count} of our top 5 revenue earners are food, not drinks."""
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. (My own question) Is the average order bigger at the counter or on the app?

    A manager deciding where to market more would want to know whether app orders are worth more than counter orders or vice versa (could be answered using dollar value or item count, I am using dollar value).
    """)
    return


@app.cell
def _(ask):
    q10_avg_order_by_channel = ask(
        """
        WITH order_totals AS (
            SELECT ol.order_id, SUM(ol.quantity * ol.price_charged) AS line_total
            FROM order_lines ol
            GROUP BY ol.order_id
        ),
        option_totals AS (
            SELECT ol.order_id, SUM(ol.quantity * lo.price_charged) AS option_total
            FROM line_options lo
            JOIN order_lines ol ON ol.line_id = lo.line_id
            GROUP BY ol.order_id
        ),
        full_totals AS (
            SELECT ot.order_id, ot.line_total + COALESCE(opt.option_total, 0) AS order_total
            FROM order_totals ot
            LEFT JOIN option_totals opt ON opt.order_id = ot.order_id
        )
        SELECT o.channel, COUNT(*) AS num_orders, ROUND(AVG(ft.order_total), 2) AS avg_order_value
        FROM orders o
        JOIN full_totals ft ON ft.order_id = o.order_id
        GROUP BY o.channel
        ORDER BY avg_order_value DESC
        """)
    q10_avg_order_by_channel
    return (q10_avg_order_by_channel,)


@app.cell
def _(q10_avg_order_by_channel):
    _rows = {r["channel"]: r for r in q10_avg_order_by_channel.iter_rows(named=True)}
    _counter = _rows["counter"]
    _app = _rows["app"]
    f"""Average order value by dollars is almost the same regardless of if a customer orders at the {"counter" if _counter["avg_order_value"] >= _app["avg_order_value"] else "app"} (${_counter['avg_order_value']:.2f} from {_counter['num_orders']} orders) or through the {"app" if _counter["avg_order_value"] >= _app["avg_order_value"] else "counter"} (${_app['avg_order_value']:.2f} from {_app['num_orders']} orders) which is only a few cents apart."""
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 1. How I Know These Numbers Are Right

    For Check 1 I'll do a total against the sum of its parts. Question 2 splits revenue into 4 categories. If I add those categories revenues back up, they should equal the total i can compute from order_lines and line_options, without any GROUP BY category at all. If question 2's query double-joined something or dropped a category, these two numbers would not agree.
    """)
    return


@app.cell
def _(ask, q2_category_margin):
    _sum_of_categories = round(q2_category_margin["revenue"].sum(), 2)
    _overall_total = ask(
        """
        SELECT ROUND(
            (SELECT SUM(quantity * price_charged) FROM order_lines)
            + (SELECT SUM(ol.quantity * lo.price_charged)
               FROM line_options lo JOIN order_lines ol ON ol.line_id = lo.line_id),
            2
        ) AS total
        """
    )["total"][0]

    assert _sum_of_categories == _overall_total, "category revenues no longer add up to the overall total"

    f"""The sum of the four category revenues is ${_sum_of_categories:,.2f} and the total computed a different way (just using SUM, no category grouping) is ${_overall_total:,.2f}. These numbers agree, but if they didnt, the assert function above would stop the notebook. For example, if Question 2's join used the wrong key, it would drop or double the option revenue, and this check would fail."""
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For Check 2 I'll do a count against the row counts and data from Part A. I know from Part A that make_data.py intentiaonlly created three members (Brent, Gabriel, and Rachel, member_ids 48, 49 and 50) who join but had never actually ordered, so question 5 should find exactly those three as well.
    """)
    return


@app.cell
def _(q5_never_ordered):
    _found_ids = set(q5_never_ordered["member_id"].to_list())
    _expected_ids = {48, 49, 50}

    assert _found_ids == _expected_ids, "question 5 no longer finds the three members Part A made with no orders"

    f"""Question 5 found member_ids {sorted(_found_ids)}, and Part A's generator made exactly {sorted(_expected_ids)} with no orders. They match, and the assert function would fail if Question 5's join (like if it did an inner join instead of a left join) stopped finding them."""
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 2. Working With the Agent

    While building the data in Part A, my agent's first version of make_data.py put the price of "Whole Milk" below its cost (free to the customer, but it still cost the business something to make), which was breaking the same "price never below cost" rule I'd made for only products, not options. I caught it when I read options.csv before committing, and changed make_data.py so "Whole Milk" is priced at $0 cost and $0 price instead, which is an actual zero rather than a loss. That fix was in the db: part A commit, in the option_catalog list near the top of make_data.py.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 3. Reading It Back

    Every order's payments checked against its total, and a list of the orders where they do not match. It needs the three tables order_lines, line_options and payments.

    **My prediction**

    To check a payment against its order total, the query has to rebuild that total from order_lines left joined with line_options on line_id (a line with no options shows up once, a line with options shows up once per option). Then it joins that to payments on order_id, before it GROUPS BY. A single order can have more than one payment such as half paid with card and half with cash, so this join can multiply rows again.
    I already know from part A, that order_lines left joined with line_options which is about 3,369 rows. I also know payments has 1,446 rows from its 1,200 orders, which is about 1.2 payments per order on average.
    Joining to payments on order_id turns each of those 3,369 rows into about 1.2 rows, since that's the average number of payments an order has. So I predict that theres around 3,369 × 1.2 = 4,040 rows before any grouping.
    """)
    return


@app.cell
def _(ask):
    reading_it_back_joins = ask(
        """
        SELECT ol.*, lo.option_id, lo.price_charged AS option_price_charged, p.*
        FROM order_lines ol
        LEFT JOIN line_options lo ON lo.line_id = ol.line_id
        JOIN payments p ON p.order_id = ol.order_id
        """)
    reading_it_back_joins.height
    return (reading_it_back_joins,)


@app.cell(hide_code=True)
def _(mo, reading_it_back_joins):
    _actual = reading_it_back_joins.height
    _predicted = 4040
    _diff = _actual - _predicted
    mo.md(
        f"""
    Did my prediction match?
    I predicted about {_predicted:,} rows but the joins alone actually produce {_actual:,} rows, {_diff:,} more than I predicted. They're close, and the gap makes sense because I used two averages, the "about half of lines have no options" and "about 1.2 payments per order" but the real data doesn't split exactly down the middle, so the actual count is a little above my estimate.

    What one row of this result means: 
    One row of this result is a single order line (one product on one order), that is joined to one of its options if it has one, and also joined to one of that order's payments. So one real order, for example, a latte with oat milk paid for with one card is exactly one row in here. But an order that has two line items and two payments (like half cash and half card) becomes four rows (2 lines × 2 payments), even though it's only one order. That's why the answer to question 4 (above) doesn't use the raw join, it totals each order's lines-plus-options in one step first and its payments in another. This makes it so every order is counted once, not once per combination of its lines and payments.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 4. Going Further

    I graphed Question 6's monthly points-share to see if it trends up or down over the year.
    """)
    return


@app.cell
def _(alt, mo, q6_points_share):
    going_further_chart = mo.ui.altair_chart(
        q6_points_share.plot.line(
            x=alt.X("month", title="Month"),
            y=alt.Y("points_share", title="Share of orders paid partly with points"),
        ).properties(title="Points-payment share by month")
    )
    going_further_chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    It fluctuates between about 21% and 36% most months with no clear upward or downward trend. It doesnt climb steadily as the loyalty program continues, because make_data.py gets each order's payment method seperately every time rather than showing the points over the year. A real cafe with a growing loyalty program might want to show that climbing trend instead, and if I wanted that, I'd change make_data.py to make the points usage depend on how long a member had been enrolled.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 5. Time Spent

    I spent about 4-5 hours on part A and 4-5 hours on part B
    """)
    return


if __name__ == "__main__":
    app.run()
