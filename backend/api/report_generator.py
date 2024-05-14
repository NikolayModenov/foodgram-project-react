from django.utils import timezone, dateformat


def format_shopping_cart_report(shopping_cart):
    '''Format the shopping list into text for download.'''
    for_download = list()
    for i, ingredient in enumerate(shopping_cart):
        name = ingredient['recipe__ingredients__product__name']
        amount = ingredient['amount']
        measurement_unit = ingredient[
            'recipe__ingredients__product__measurement_unit'
        ]
        recipes = ingredient['recipes']
        for_download.append(
            f'{i+1}. {name.capitalize()} = {amount} {measurement_unit}. '
            f'Нужно для: {recipes}\n'
        )
    time_now = dateformat.format(
        timezone.localtime(timezone.now()), 'Y-m-d H:i:s'
    )
    for_download.append(f'Дата создания: {time_now}')
    return for_download
