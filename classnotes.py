reply = {
    
    "count": 2,
    "data": [
        {"name": "Carla", "city": "Boston", "age": 34},
        {"name": "Hiro", "city": "Austin", "age": 29},
        {"name": "Maria", "city": "Denver", "age": 41},
        {"name": "Jamal", "city": "Seattle", "age": 23},
        {"name": "Priya", "city": "Chicago", "age": 37},
    ],
}


for row in reply['data']:
    if row['name'] == 'Ethan':
        print(f'Found {row["name"]}, {row["city"]}, {row["age"]}')
#Dont find Ethan


#Found Priya
for row in reply['data']:
    if row['name'] == 'Priya':
        print(f'Found {row["name"]}, {row["city"]}, {row["age"]}')


patients = [20, 25, 18, 30, 22, 27, 35]
#change into for loop
for bmi in patients:
    if bmi >= 30:
        category = "Obese"
    elif bmi >= 25:
        category = "Overweight"
    elif bmi >= 18.5:
        category = "Normal"
    else:
        category = "Underweight"
    print(category)