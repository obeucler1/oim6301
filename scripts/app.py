
#import bmi


#result = bmi.compute_bmi(70, 1.75)
#print(f"Computed BMI: {result: .2f}")



from scripts import bmi


people = [
    {"name": "Carla", "height": 1.65, "weight": 60},
    {"name": "Hiro", "height": 1.78, "weight": 75},
    {"name": "Maria", "height": 1.70, "weight": 68},
    {"name": "Jamal", "height": 1.82, "weight": 80},
    {"name": "Priya", "height": 1.60, "weight": 55},
    {"name": "Liam", "height": 1.75, "weight": 72},
    {"name": "Noor", "height": 1.68, "weight": 63},
    {"name": "Felix", "height": 1.90, "weight": 90},
]

for person in people:
    weight = person["weight"]
    height = person["height"]
    bmi_value = bmi.compute_bmi(weight, height)
    category = bmi.classify_bmi(bmi_value)
    