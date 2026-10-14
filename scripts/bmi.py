
#Question Wrap the code into a function
def classify_bmi(bmi):
    #print(bmi)
    if bmi >= 30:
        category = "Obese"
    elif bmi >= 25:
        category = "Overweight"
    elif bmi >= 18.5:
        category = "Normal"
    else:
        category = "Underweight"
    return(category)

#bmiValue = 27
#classify_bmi(bmiValue)

#In terminal run "uv run scripts/bmi.py"

bmi_value = 18
result = classify_bmi(bmi_value)
print(f"Your category is {result}.")
#Gives you outputs of "Underweight" and "Your category is None."
# Have to change inside def, print(category) to return(category)

