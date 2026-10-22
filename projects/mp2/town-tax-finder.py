import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import csv

    import altair as alt
    import polars as pl
    import requests

    return (requests,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question:
    Who would use this, and what decision does it help them make? (Two or three sentences, in words somebody outside this course would understand.)


    Someone who would use this would be a buyer that is looking at houses to buy in the Middlesex county, and wants to only look at houses below a specific property tax.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI.
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
    First I would write the get() function for the csv file of the API's Massachussetes data from state's Division of Local Services so it is connected to this notebook. Then I would examine the dataset so I would use def function to be able to write a cell that will get the information I ask from the dataset. After that, I would write a for loop that takes only the county, town, and budgets and assign the column names to a variable then using that, create the csv file. After that, I would be able to write a for loop that grabs each town in the Middlesex county within that tax range. Then I would make the for loop county and budget be interactive for the user to input their own county and budget range if they want to look somewhere else.

    1. My tool will need the get() function to get the information from the API, then the def function to get the county and budgets using its parameters, then ill need to a for loop to go through each town in the dataset and then the functions for creating the csv. I would also need the pl.read_csv to look at the csv and use .filter() with .group_by , .sort(), and .agg(), to get a list of towns within that budget.
    2. They will request the csv file that I will create that includes the countys, towns, and the tax bill.
    3. I will know I have every record because I can check my csv file total rows with the total number on the API.
    4. I will use a SQL check in section 6 and the towns listed and tax's numbers should match each other.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs.

    Every input in one cell.
    """)
    return


@app.cell
def _(mo):
    county_input = mo.ui.text(value="Middlesex", label="County")
    budget_input = mo.ui.number(value=700000, label="Max average home value ($)")
    tax_limit_dollars = 8000 
    fiscal_year = 2026 
    mo.vstack([county_input, budget_input])
    return budget_input, county_input, fiscal_year, tax_limit_dollars


@app.cell
def _(budget_input, county_input):
    county = county_input.value
    budget_dollars = budget_input.value
    return budget_dollars, county


@app.cell
def _(requests):
    def get_towns(county): 
        first_reply = requests.get( 
            "https://oim.zhili.dev/ma/towns", 
            params={"county": county, "per_page": 100}, 
            timeout=10,).json() 
        towns = first_reply["items"] 
        pages = first_reply["pagination"]["pages"] 

        for page in range(2, pages + 1): 
            page_reply = requests.get( 
                "https://oim.zhili.dev/ma/towns", 
                params={"county": county, "per_page": 100, "page": page}, 
                timeout=10, 
            ).json() 
            for town in page_reply["items"]: 
                towns.append(town) 
        return towns 

    return (get_towns,)


@app.cell
def _(county, get_towns):
    ma_towns = get_towns(county) 
    len(ma_towns) 
    return (ma_towns,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work.

    Your functions, and the code that uses them.
    """)
    return


@app.cell
def _(requests):
    def get_town_history(dor_code, fiscal_year): 
        history_reply = requests.get( 
            f"https://oim.zhili.dev/ma/towns/{dor_code}/history", 
            params={"from_year": fiscal_year, "to_year": fiscal_year}, 
            timeout=10, 
        ).json() 
        years = history_reply["years"] 
        if len(years) == 0: 
            return None 
        return years[0] 

    return (get_town_history,)


@app.cell
def _(
    budget_dollars,
    fiscal_year,
    get_town_history,
    ma_towns,
    tax_limit_dollars,
):
    matchingTowns = []
    for town in ma_towns:
        history = get_town_history(town["dor_code"], fiscal_year)
        if history is None:
            continue
        familyValue = history["average_single_family_value_dollars"]
        rate = history["residential_rate_per_thousand"]
        bill = history["average_single_family_bill_dollars"]
        if familyValue <= budget_dollars and bill <= tax_limit_dollars:
            matchingTowns.append({"town": town["name"], "average home value": familyValue, "residential tax rate": rate, "average bill": bill})

    len(matchingTowns)
    return (matchingTowns,)


@app.function
def get_bill(town):
    return town["average bill"]


@app.cell
def _(matchingTowns):
    matchTownsSort = sorted(matchingTowns, key=get_bill)
    matchTownsSort
    return (matchTownsSort,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer.

    Your result table, printed with print and f-strings with the columns lined up, and **one sentence that answers the question in section 1** with the numbers in it.

    **Print the sentence from code with an f-string, so that it changes when the data does.**
    """)
    return


@app.cell
def _(matchTownsSort):
    for towns in matchTownsSort:
        print(f"{towns["town"]:<15}Avg Home Value: {towns["average home value"]:>7}       Residential Tax Rate: {towns["residential tax rate"]:>6}             Avg Bill: {towns["average bill"]:>5}")

    return


@app.cell
def _(budget_dollars, county, matchTownsSort):
    cheaptestTown = matchTownsSort[0]
    print(f"For a homebuyer who wants a home in {county} with a budget of ${budget_dollars:,}, the town with the lowest average tax bill of ${cheaptestTown['average bill']:,} is {cheaptestTown['town']}.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.  How I Know These Numbers Are Right.

    Reach at least one result a second way, in this notebook, and show that the two agree. Write a cell that gets the same number from other fields, or open the raw reply in your browser and find each number of one row of your table there. For instance: an average bill is close to the average value times the tax rate divided by 1,000; an order's total equals the sum of its lines; the number of records you collected equals the total the API reports. At least one of those checks runs as code, and shows both numbers.
    """)
    return


@app.cell
def _(requests):
    def get_towns_check(county, name ): 
        first_reply = requests.get( 
            "https://oim.zhili.dev/ma/towns", 
            params={"county": county, "per_page": 100}, 
            timeout=10,).json() 
    
        towns = first_reply["items"] 
        for town in towns:
            if town["name"] == name:
                return town
        return None

    return (get_towns_check,)


@app.cell
def _(get_towns_check):
    get_towns_check('Middlesex', 'Malden')

    return


@app.cell
def _(requests):
    def dor_code_check(dor_code):
        town_reply = requests.get(
            f"https://oim.zhili.dev/ma/towns/{dor_code}",
            timeout=10,
        ).json()
        return town_reply

    return (dor_code_check,)


@app.cell
def _(dor_code_check):
    dor_code_check("165")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I checked my numbers by defining a new variable called get_towns_check() where I took the data from /ma/towns and then passed Middlesex and Malden through it to get its information. From there, I made another def function with the /ma/towns/{dor_code} to get the latest finanes information for a specific dor_code. Then, I used the dor code from Malden (165) to get the information from the API and saw that the Average Home Value was $434420, the Residential Tax Rate was 11.4 (per thousand) and the Average Single Family Bill was $4952 which are all consistent with the above outputs I got.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent.

    Pick one piece of AI output you did not accept as-is. What did it give you, what did you change, and how did you know? Point to the commit or the cell. If the agent got it right the first time: What did you do to verify that? Pointing to your check in section 6 is enough.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In the first cell in my "Inputs" section, I had inputted the values given to us in the directions (county = "Middlesex", budget_dollars = 700000, tax_limit_dollars = 8000, fiscal_year = 2026). As I was going through the next sections, I remembered that we had to make the code able to have the county and budget numbers changed if needed. I tried it myself, but ultimately asked my agent to help. My agent changed all 4 variables (county, budget_dollars, tax_limit_dollars, and fiscal_year) to inputs. I thought this was a good idea in theory, but the directions stated we only needed budget and county to be inputs. I then overrided my Agents code for tax_limit_dollars and fiscal_year to stay as fixed numbers of 8000 and 2026.
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
    My agent helped me write the first cell in the Inputs section.
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
