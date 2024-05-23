import json

base_data = json.load(open(
    "data/base.json", "r", encoding="utf-8"))

for data in base_data:
    if data['model'] == 'recipe.product':
        data["fields"]["ingredient"] = data["fields"].pop('product')
        print(f'data = {data["fields"]}')

with open('base3.json', 'w') as fp:
    json.dump(base_data, fp)
