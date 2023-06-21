

from tabulate import tabulate
import csv
import sys


def parse_meal_plan(meal_plan_file_path):
    # Read the meal plan from the file
    with open(meal_plan_file_path, 'r') as meal_plan_file:
        meal_plan_table = meal_plan_file.read()

    # Parse the meal plan table and extract the recipe names
    meal_plan = [row.split("|")[1:-1]
                 for row in meal_plan_table.split("\n") if "|" in row]

    meal_plan = meal_plan[-7:]

    for i in range(7):
        meal_plan[i][0] = meal_plan[i][0].strip().lower()
        meal_plan[i][1] = meal_plan[i][1].strip().lower()

    return meal_plan


def parse_ingredient_file(ingredients_file_path):
    ingredient_info = {}

    try:
        with open(ingredients_file_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                ingredient_name = row['Ingredient Name'].strip().lower()
                ingredient_info[ingredient_name] = {
                    'Dutch Name': row['Dutch Name'],
                    'Supermarket Link': row['Supermarket Link'],
                    'Available at Farmers Market': row['Available at Farmers Market'] == 'true',
                    'Amount': row['Amount'],
                    'Unit': row['Unit']
                }
    except FileNotFoundError:
        pass

    return ingredient_info


def parse_recipe_file(recipe_file_path):
    with open(recipe_file_path, 'r') as recipe_file:
        recipe_lines = recipe_file.readlines()

    recipes = {}
    current_recipe = None

    for line in recipe_lines:
        line = line.strip()

        if line.startswith('## '):
            current_recipe = line[3:].strip().lower()
            recipes[current_recipe] = []
        elif current_recipe and line.startswith('* [ ] '):
            ingredient = line[6:].strip().lower()
            recipes[current_recipe].append(ingredient)

    return recipes


def assemble_grocery_list(meal_plan, recipes):
    # Create an empty dictionary to store the combined ingredients and their quantities
    grocery_list = {}

    # For each recipe in the meal plan
    for meal in meal_plan:
        # Assuming the recipe name is in the first column
        recipe_name = meal[1]

        if '+' in recipe_name:
            compound_recipe = recipe_name.split('+')
            for sub_recipe in compound_recipe[1:]:
                meal_plan.append(['sub', sub_recipe.strip()])
            recipe_name = compound_recipe[0].strip()

        if recipe_name in recipes:
            for ingredient in recipes[recipe_name]:
                ingredient_name = ingredient
                quantity = 1
                unit = ''

                if ingredient[0].isnumeric():
                    # Split the line into quantity and ingredient name
                    ingredient_parts = ingredient.split(' ', 1)
                    unit = ingredient_parts[0].lstrip('0123456789.')
                    quantity = float(
                        ingredient_parts[0][0:len(ingredient_parts[0])-len(unit)])
                    ingredient_name = ingredient_parts[1]

                # Check if the ingredient is already in the grocery list
                if ingredient_name in grocery_list:
                    # If it exists, add the quantity to the existing quantity
                    grocery_list[ingredient_name][0] += quantity
                else:
                    # If it's a new ingredient, add it to the grocery list
                    grocery_list[ingredient_name] = [quantity, unit]
        else:
            print(f"recipe \"{recipe_name}\" not found in the recipe list")

    return grocery_list


def enhance_grocery_list(grocery_list, ingredient_info):
    groceries = []
    for item in grocery_list:
        if item in ingredient_info:
            groceries.append({
                'name': item,
                'quantity': grocery_list[item][0],
                'unit': grocery_list[item][1],
                'dutch': ingredient_info[item]['Dutch Name'],
                'market': ingredient_info[item]['Available at Farmers Market'],
                'ah_link': ingredient_info[item]['Supermarket Link'],
                'ah_amount': ingredient_info[item]['Amount'],
                'ah_unit': ingredient_info[item]['Unit'],
            })
        else:
            groceries.append({
                'name': item,
                'quantity': grocery_list[item][0],
                'unit': grocery_list[item][1]
            })
    return groceries


path = sys.argv[1]

meal_plan = parse_meal_plan(path + "/Meal Plan.txt")
recipes = parse_recipe_file(path + "/Recipes.txt")
grocery_list = assemble_grocery_list(meal_plan, recipes)

ingredient_info = parse_ingredient_file(path + "/ingredients.csv")
groceries = enhance_grocery_list(grocery_list, ingredient_info)

# Print the combined grocery list
print("Groceries without extra data:")
for ingredient in groceries:
    if not 'market' in ingredient:
        print(
            f"* [ ] {ingredient['name']}: {ingredient['quantity']}{ingredient['unit']}")

print("\n## AH")
for ingredient in groceries:
    if 'market' in ingredient and not ingredient['market']:
        if ingredient['unit'] == ingredient['ah_unit']:
            print(
                f"* [ ] {ingredient['name']}: {int(ingredient['quantity']) / int(ingredient['ah_amount'])} x {ingredient['ah_link']}")
        else:
            print(
                f"* [ ] {ingredient['name']}: {ingredient['quantity']}{ingredient['unit']} of {ingredient['ah_link']}")

print("\n## Market")
for ingredient in groceries:
    if 'market' in ingredient and ingredient['market']:
        print(
            f"* [ ] {ingredient['dutch']}: {ingredient['quantity']}{ingredient['unit']}")
