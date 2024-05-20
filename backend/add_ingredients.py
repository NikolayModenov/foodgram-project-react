import json

from recipe.models import Ingredient

ingredients_data = json.load(open(
    "data/ingredients.json", "r", encoding="utf-8")
)
print(f'data = {ingredients_data}')
for i in range(len(ingredients_data)):
    print(f'unit = {i}')
    ingredient = Ingredient(
        id=i, name=ingredients_data[i]['name'],
        measurement_unit=ingredients_data[i]['measurement_unit']
    )
    ingredient.save()
