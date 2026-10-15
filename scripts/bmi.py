## 10/14, Slide 9



#Question 4 
    # Wrap the code into a function
def classify_bmi(bmi):
    ''' Classify the BMI into categories.'''
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

def compute_bmi(weight, height):
    bmi = weight / (height ** 2)
    return bmi

def main():
    weight= float(input("Enter your weight in kgs:" ))
    height = float(input("Enter your height in meters:" ))
    bmi_value = compute_bmi(weight, height)
    result = classify_bmi(bmi_value)
    print(f"Your BMI is {bmi_value:.2f}, and your category is {result}")

#main()
if __name__ == "__main__":
    main()