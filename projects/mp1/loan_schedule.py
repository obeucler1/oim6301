# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
# ]
# ///
"""Mini Project 1.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mini Project 1

    Your choice of project, what each one asks for, the due date and how it is graded are on the Mini Project 1 page of the course site, linked from the calendar. This notebook is the shape to build it in. Keep the headings, and replace each line in italics with your own.

    Save it in your course repository as `projects/mp1/<your-tool>.py`, named for what it does, such as `loan-schedule.py`, and open it with `uv run marimo edit`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question

    A person who would use this would be someone that wants to buy an apartment or home and is trying to figure out how many years to pay off their loans. We could also use this for cars or other assets that have loans associated with them.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI


    My loop would carry the monthly loan percentage through each month to see how much the buyer would pay each month, along with the total amount they would pay once they've paid the full mortgage.

    To check this, I would compare the final amount paid against the expected amount paid based on the loan amount and the interest rate per month.

    *Commit this notebook with the message `mp1: plan before AI`.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs

    Every number the project starts from goes in the cell below, and nowhere else, so that changing one input changes every result after it.

    Copy in the default inputs for your project from the Mini Project 1 page. If you chose your own project, type your data in here, or ask your agent to generate it with `faker`. The required part reads no file.
    """)
    return


@app.cell
def _():
    # Your inputs.

    loan_amount = 400000
    annual_rates = {30: 0.0703, 15: 0.0642}
    return (loan_amount,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    Add as many cells as you need. Try each step yourself before you ask your agent, and commit as you go.
    """)
    return


@app.cell
def _(loan_amount):
    # r = annual rate of the term, n = number of months

    rThirty = 0.0703 / 12
    nThirty = 12 * 30
    range(1, nThirty + 1) 
    loan30 = loan_amount * rThirty / (1 - (1 + rThirty) ** -nThirty)
    loan30 = round(loan30, 2)
    print (f"Monthly payment for 30 years for each term is ${loan30}")
    return loan30, nThirty, rThirty


@app.cell
def _(loan_amount):
    rFifteen = 0.0642 / 12
    nFifteen = 12 * 15
    loan15 = loan_amount * rFifteen / (1 - (1 + rFifteen) ** -nFifteen)
    loan15 = round(loan15, 2)
    print (f"Monthly payment for 15 years for each term is ${loan15}")
    return loan15, nFifteen, rFifteen


@app.cell
def _(loan30, loan_amount, nThirty, rThirty):
    # Build the month-by-month schedule for the 30-year loan.
    # balance is what the loop carries from one month to the next.
    # _m, _interest, _payment, _principal are private to this cell (underscore prefix)
    # because sched15's cell uses the same loop variable names.

    sched30 = []
    balance = loan_amount
    for _m in range(1, nThirty + 1):
        _interest = round(balance * rThirty, 2)
        _payment = loan30
        _principal = round(_payment - _interest, 2)
        if _m == nThirty or _principal >= balance:
            # last month: pay off exactly what's left, overriding rounding drift
            _principal = balance
            _payment = round(_principal + _interest, 2)
        balance = round(balance - _principal, 2)
        sched30.append({"month": _m, "payment": _payment, "interest": _interest, "principal": _principal, "balance": balance})

    sched30
    return (sched30,)


@app.cell
def _(loan15, loan_amount, nFifteen, rFifteen):
    # Build the month-by-month schedule for the 15-year loan.
    # balance is what the loop carries from one month to the next.

    sched15 = []
    balance15 = loan_amount
    for m in range(1, nFifteen + 1):
        interest = round(balance15 * rFifteen, 2)
        payment = loan15
        principal = round(payment - interest, 2)
        if m == nFifteen or principal >= balance15:
            # last month: pay off exactly what's left, overriding rounding drift
            principal = balance15
            payment = round(principal + interest, 2)
        balance15 = round(balance15 - principal, 2)
        sched15.append({"month": m, "payment": payment, "interest": interest, "principal": principal, "balance": balance15})

    sched15
    return (sched15,)


@app.cell
def _(sched30):
    totalInt = 0
    for row in sched30:
        totalInt = totalInt + row["interest"]
    totalInt = round(totalInt, 2)
    print(f"The total interest for the 30 year loan is ${totalInt}")
    return (totalInt,)


@app.cell
def _(sched15):
    totalInt15 = 0
    for row15 in sched15:
        totalInt15 = totalInt15 + row15["interest"]
    totalInt15 = round(totalInt15, 2)
    print(f"The total interest for the 15 year loan is ${totalInt15}")
    return (totalInt15,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer

    *A table of your results in the cell below, printed with `print` and f-strings, then one sentence here that answers the question in section 1, with the number in it.*
    """)
    return


@app.cell
def _(sched30):
    print("30-year loan schedule:")
    print(f"{'month':>5} {'payment':>10} {'interest':>10} {'principal':>10} {'balance':>12}")
    for _row in sched30:
        print(f"{_row['month']:>5} {_row['payment']:>10,.2f} {_row['interest']:>10,.2f} {_row['principal']:>10,.2f} {_row['balance']:>12,.2f}")
    return


@app.cell
def _(sched15):
    print("15-year loan schedule:")
    print(f"{'month':>5} {'payment':>10} {'interest':>10} {'principal':>10} {'balance':>12}")
    for _row15 in sched15:
        print(f"{_row15['month']:>5} {_row15['payment']:>10,.2f} {_row15['interest']:>10,.2f} {_row15['principal']:>10,.2f} {_row15['balance']:>12,.2f}")
    return


@app.cell
def _(loan15, loan30, totalInt, totalInt15):
    print(f"For someone who is buying a house or apartment, if they have $40,000 in mortgages to pay and are trying to choose between the 30-year (payment ${loan30:,.2f}, total interest: ${totalInt:,.2f} and the 15-year (payment ${loan15:,.2f}, total interest: ${totalInt15:,.2f}) I would have them choose the 15 year payment, even if it is more money per month.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right

    *At least one check that reaches a result a second, independent way. Name what you compared and what came out.*
    """)
    return


@app.cell
def _(loan15, loan30, loan_amount, totalInt, totalInt15):
    # (payment * number of months) - loan amount

    check1 = (loan30 * 360) - loan_amount
    check2 = (loan15 * 180) - loan_amount

    check1 = round(check1, 2)
    check2 = round(check2, 2)

    print(f"From my own math, I got ${check1} which is close to ${totalInt} and ${check2} which is close to ${totalInt15} from my loops")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    I asked my agent to double check the schedule data, and it says that it accidentally wrote "if _principal > balance:" which is not true in this problem since we wanted it to stop at zero, not to stop only if it was overpaid. My agent then adjusted the line to "if _m == nThirty or _principal >= balance:" which then made sure the last row of each schedule ended at 0.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Going Further

    I am going to solve "Pay an extra $200 every month. How many months, and how much interest, does that save on each loan?"
    """)
    return


@app.cell
def _(loan30, loan_amount, nThirty, rThirty, totalInt):
    # Extra $200/month on the 30-year loan, using a for loop instead of a while loop.
    # Paying extra can only pay off the loan faster, never slower, so looping up to
    # nThirty months is always enough. The "if balanceExtra > 0" skips any months
    # after the loan is already paid off, so months30Extra only counts real months.

    extra = 200
    balanceExtra = loan_amount
    totalInt30Extra = 0
    months30Extra = 0
    for _m in range(1, nThirty + 1):
        if balanceExtra > 0:
            interestExtra = round(balanceExtra * rThirty, 2)
            paymentExtra = loan30 + extra
            principalExtra = round(paymentExtra - interestExtra, 2)
            if principalExtra >= balanceExtra:
                principalExtra = balanceExtra
            balanceExtra = round(balanceExtra - principalExtra, 2)
            totalInt30Extra = round(totalInt30Extra + interestExtra, 2)
            months30Extra = months30Extra + 1

    monthsSaved30 = nThirty - months30Extra
    interestSaved30 = round(totalInt - totalInt30Extra, 2)

    print(f"30-year with extra $200/month: paid off in {months30Extra} months instead of {nThirty}")
    print(f"That saves {monthsSaved30} months and ${interestSaved30} in interest")
    return (extra,)


@app.cell
def _(extra, loan15, loan_amount, nFifteen, rFifteen, totalInt15):
    # Extra $200/month on the 15-year loan. Same idea as the 30-year version above.

    balance15Extra = loan_amount
    totalInt15Extra = 0
    months15Extra = 0
    for _m15 in range(1, nFifteen + 1):
        if balance15Extra > 0:
            interest15 = round(balance15Extra * rFifteen, 2)
            payment15 = loan15 + extra
            principal15 = round(payment15 - interest15, 2)
            if principal15 >= balance15Extra:
                principal15 = balance15Extra
            balance15Extra = round(balance15Extra - principal15, 2)
            totalInt15Extra = round(totalInt15Extra + interest15, 2)
            months15Extra = months15Extra + 1

    monthsSaved15 = nFifteen - months15Extra
    interestSaved15 = round(totalInt15 - totalInt15Extra, 2)

    print(f"15-year with extra $200/month: paid off in {months15Extra} months instead of {nFifteen}")
    print(f"That saves {monthsSaved15} months and ${interestSaved15} in interest")
    return


if __name__ == "__main__":
    app.run()
