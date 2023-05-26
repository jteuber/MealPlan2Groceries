

from tabulate import tabulate
import csv


def parse_meal_plan(meal_plan_file_path):
    # Read the meal plan from the file
    with open('meal_plan.md', 'r') as meal_plan_file:
        meal_plan_table = meal_plan_file.read()

    # Parse the meal plan table and extract the recipe names
    meal_plan = tabulate([row.split("|")[1:-1] for row in meal_plan_table.split("\n")
                          if "|" in row], headers="firstrow", tablefmt="pipe")

    return meal_plan


def parse_ingredient_file(ingredients_file_path):
    ingredient_info = {}

    with open(ingredients_file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            ingredient_name = row['Ingredient Name']
            ingredient_info[ingredient_name] = {
                'Dutch Name': row['Dutch Name'],
                'Supermarket Link': row['Supermarket Link'],
                'Available at Farmers Market': row['Available at Farmers Market']
            }

    return ingredient_info


def parse_recipe_file(recipe_file_path):
    with open(recipe_file_path, 'r') as recipe_file:
        recipe_lines = recipe_file.readlines()

    recipes = {}
    current_recipe = None

    for line in recipe_lines:
        line = line.strip()

        if line.startswith('## '):
            recipe_name = line[3:]
            current_recipe = recipe_name
            recipes[current_recipe] = []
        elif current_recipe and line.startswith('* [ ] '):
            ingredient = line[7:]
            recipes[current_recipe].append(ingredient)

    return recipes


def assemble_grocery_list(meal_plan, recipes):
    # Create an empty dictionary to store the combined ingredients and their quantities
    grocery_list = {}

    # For each recipe in the meal plan
    for meal in meal_plan:
        # Assuming the recipe name is in the first column
        recipe_name = meal[1]

        if recipe_name in recipes:
            for ingredient in recipes[recipe_name]:
                # Split the line into quantity and ingredient name
                ingredient_parts = ingredient.split(' ', 1)
                quantity = ingredient_parts[0]
                ingredient_name = ingredient_parts[1]

                # Check if the ingredient is already in the grocery list
                if ingredient_name in grocery_list:
                    # If it exists, add the quantity to the existing quantity
                    grocery_list[ingredient_name] += quantity
                else:
                    # If it's a new ingredient, add it to the grocery list
                    grocery_list[ingredient_name] = quantity

    return grocery_list


def enhance_grocery_list(grocery_list, ingredient_info):
    groceries = []
    for item in grocery_list:
        if item in ingredient_info:
            groceries.append({
                'name': item,
                'quantity': grocery_list[item],
                'Dutch Name': ingredient_info[item]['Dutch Name'],
                'Supermarket Link': ingredient_info[item]['Supermarket Link'],
                'Available at Farmers Market': ingredient_info[item]['Available at Farmers Market']
            })
        else:
            groceries.append({
                'name': item,
                'quantity': grocery_list[item]
            })


meal_plan = parse_meal_plan("Meal Plan.txt")
recipes = parse_recipe_file("Recipes.txt")
grocery_list = assemble_grocery_list(meal_plan, recipes)

ingredient_info = parse_ingredient_file("ingredients.csv")


# Print the combined grocery list
for ingredient, quantity in grocery_list:
    print(f"{ingredient}: {quantity}")
