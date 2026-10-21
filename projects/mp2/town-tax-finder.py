import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Question:
    Who would use this, and what decision does it help them make? (Two or three sentences, in words somebody outside this course would understand.)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##My Plan Before AI.
    Before you ask your agent anything, open the API's address in your browser and read what comes back. Then write how you would solve it: the steps, in order, in plain words, in five lines or more. Then answer these:

    1. Which functions will your tool need? For each, what goes in and what comes out?

    2. Which addresses will they request?

    3. How will you know you have every record?

    4. Which check will you use in section 6, and which two numbers should agree?

    **Commit with the message mp2: plan before AI.**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Inputs.

    Every input in one cell.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Work.

    Your functions, and the code that uses them.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##The Answer.

    Your result table, printed with print and f-strings with the columns lined up, and **one sentence that answers the question in section 1** with the numbers in it.

    **Print the sentence from code with an f-string, so that it changes when the data does.**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How I Know These Numbers Are Right.

    Reach at least one result a second way, in this notebook, and show that the two agree. Write a cell that gets the same number from other fields, or open the raw reply in your browser and find each number of one row of your table there. For instance: an average bill is close to the average value times the tax rate divided by 1,000; an order's total equals the sum of its lines; the number of records you collected equals the total the API reports. At least one of those checks runs as code, and shows both numbers.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Working With the Agent.

    Pick one piece of AI output you did not accept as-is. What did it give you, what did you change, and how did you know? Point to the commit or the cell. If the agent got it right the first time: What did you do to verify that? Pointing to your check in section 6 is enough.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Reading It Back.

    Pick two functions in your notebook that your agent wrote or helped write.

    For each, write in your own words what goes in, what comes out, and one line you had to ask about.

    Then choose one change to what the tool does, such as another county, another week or another rule. Changing one value in your Inputs cell is enough.

    Write what you expect to change in the answer.

    **Commit with the message mp2: prediction**, make the change, run it, and write what happened and whether it matched.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##Going Further.

    What you tried past the main task, what you found, and where it is in the notebook.

    examples:

    - Add a second API. Bring in data from a second API and combine it with the first in whatever way makes your answer better or more interesting.
    - Let somebody use it without editing code. A marimo notebook also runs as a script, uv run python projects/mp2/<your-tool>.py. Ask for the inputs with input(), take them from the command line, or give them controls and open the notebook with uv run marimo run.
    - Put a model inside your tool. Write a function that sends the numbers your tool found to a model, with your Babson key, and returns the paragraph the model writes for your user. A paragraph you get from the chat panel or from your agent does not count. This one comes from your code each time the tool runs, so it changes when the data does.
    - Run it on a schedule. GitHub Actions can rerun the notebook every day or every week, with any key stored as a repository secret.
    - Keep what each run found, and use that history to answer something a single run cannot.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Time Spent.

    About how many hours this project took you outside class, as one number. It is not graded.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    """)
    return


if __name__ == "__main__":
    app.run()
