from flask import Flask, render_template, request, jsonify
import requests
import spacy
from spacy.cli import download

app = Flask(__name__, template_folder='.')

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Use the same ingredients list
ALL_INGREDIENTS = sorted([
    'apple', 'banana', 'bread', 'butter', 'carrot', 'cheese', 'chicken',
    'egg', 'flour', 'garlic', 'milk', 'mushroom', 'onion', 'pasta',
    'potato', 'rice', 'salt', 'sugar', 'tomato', 'oil', 'pepper',
    'spinach', 'yogurt', 'beef', 'pork', 'lettuce', 'corn', 'bell pepper',
    'cucumber', 'mayonnaise', 'mustard', 'ketchup', 'baking powder',
    'baking soda', 'vinegar', 'honey', 'jam', 'oats', 'soy sauce'
])

def get_meals_by_ingredient(ingredient):
    url = f'https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}'
    response = requests.get(url)
    data = response.json()
    return [meal['idMeal'] for meal in data['meals']] if data['meals'] else []

def get_full_recipe(meal_id):
    url = f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}'
    response = requests.get(url)
    data = response.json()
    if data and data['meals']:
        meal = data['meals'][0]
        ingredients = []
        for i in range(1, 21):
            ing = meal.get(f'strIngredient{i}')
            if ing and ing.strip():
                ingredients.append(ing.strip().lower())
        return {
            'title': meal['strMeal'],
            'instructions': meal['strInstructions'],
            'image': meal['strMealThumb'],
            'ingredient_list': ingredients
        }
    return None

# NLP parsing logic
def parse_query(text):
    doc = nlp(text.lower())
    include = set()
    exclude = set()

    exclude_mode = False
    for token in doc:
        word = token.text.strip().lower()

        # Detect negation words
        if word in ["no", "without", "exclude", "avoid"]:
            exclude_mode = True
            continue
        elif word in ["with", "including", "have", "use", "using"]:
            exclude_mode = False
            continue

        if word in ALL_INGREDIENTS:
            if exclude_mode:
                exclude.add(word)
            else:
                include.add(word)

    final_include = list(include - exclude)
    final_exclude = list(exclude)
    return final_include, final_exclude

@app.route('/')
def home():
    return render_template('index.html', ingredients=ALL_INGREDIENTS)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    selected_ingredients = data.get('selectedIngredients', [])

    if not selected_ingredients:
        return jsonify({'recipes': []})

    # TheMealDB only supports single ingredient searches in filter.php
    all_recipe_ids = []
    for ing in selected_ingredients:
        res = requests.get(f'https://www.themealdb.com/api/json/v1/1/filter.php?i={ing}')
        json_data = res.json()
        meals = json_data.get('meals')
        if meals:
            ids = [meal['idMeal'] for meal in meals]
            all_recipe_ids.append(set(ids))
        else:
            all_recipe_ids.append(set())

    if not all_recipe_ids or any(len(s) == 0 for s in all_recipe_ids):
        return jsonify({'recipes': []})

    # Intersection of all sets
    common_ids = set.intersection(*all_recipe_ids)

    if not common_ids:
        return jsonify({'recipes': []})

    # Get recipe details for first few common results
    recipes = []
    for meal_id in list(common_ids)[:5]:
        res = requests.get(f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}')
        meal = res.json().get('meals')[0]

        ingredients = []
        for i in range(1, 21):
            ing = meal.get(f'strIngredient{i}')
            measure = meal.get(f'strMeasure{i}')
            if ing and ing.strip():
                ingredients.append(f"{ing} - {measure}")

        recipes.append({
            'title': meal['strMeal'],
            'image': meal['strMealThumb'],
            'instructions': meal['strInstructions'],
            'ingredient_list': ingredients
        })

    return jsonify({'recipes': recipes})

@app.route('/nlp')
def nlp_page():
    return render_template('nlp.html')

@app.route("/nlp_search", methods=["POST"])
def nlp_search():
    data = request.get_json()
    query = data.get("query", "")
    included, excluded = parse_query(query)

    results = []
    checked_ids = set()

    for ingredient in included:
        response = requests.get(f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}")
        if response.status_code != 200 or not response.json()["meals"]:
            continue
        for meal in response.json()["meals"]:
            meal_id = meal["idMeal"]
            if meal_id in checked_ids:
                continue
            checked_ids.add(meal_id)

            # Get full recipe details
            detail_res = requests.get(f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}")
            if detail_res.status_code != 200 or not detail_res.json()["meals"]:
                continue

            meal_detail = detail_res.json()["meals"][0]
            ingredient_list = []
            for i in range(1, 21):
                ing = meal_detail.get(f"strIngredient{i}")
                if ing and ing.strip():
                    ingredient_list.append(ing.strip().lower())

            # Exclude if any excluded ingredient appears in full or part
            found_excluded = False
            for ex in excluded:
                for ing in ingredient_list:
                    if ex in ing:
                        found_excluded = True
                        break
                if found_excluded:
                    break

            if found_excluded:
                continue  # Skip this recipe

            results.append({
                "title": meal_detail["strMeal"],
                "image": meal_detail["strMealThumb"],
                "instructions": meal_detail["strInstructions"],
                "ingredient_list": ingredient_list
            })

    return jsonify({"recipes": results, "included": included, "excluded": excluded})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Use Render's assigned port
    app.run(host="0.0.0.0", port=port)
