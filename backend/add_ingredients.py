import json

from recipe.models import Ingredient, Product

# ingredients_data = json.load(open(
#     "data/ingredients.json", "r", encoding="utf-8")
# )
# print(f'data = {ingredients_data}')
# for i in range(len(ingredients_data)):
#     print(f'unit = {i}')
#     ingredient = Ingredient(
#         id=i, name=ingredients_data[i]['name'],
#         measurement_unit=ingredients_data[i]['measurement_unit']
#     )
#     ingredient.save()

base_data = json.load(open(
    "data/base.json", "r", encoding="utf-8"))

# print(f'data = {type(base_data)}')
for data in base_data:
    if data['model'] == 'recipe.product':
        data["fields"]["ingredient"] = data["fields"].pop('product')
        print(f'data = {data["fields"]}')

with open('base3.json', 'w') as fp:
    json.dump(base_data, fp)
