from django.utils import timezone, dateformat


def format_shopping_cart_report(shopping_cart):
    '''Format the shopping list into text for download.'''

    time_now = dateformat.format(
        timezone.localtime(timezone.now()), 'Y-m-d H:i:s'
    )

    ingredients = [
        f'{i}) {ingredient["name"].capitalize()} = {ingredient["amount"]} '
        f'{ingredient["unit"]}.'
        for i, ingredient in enumerate(shopping_cart, 1)
    ]

    recipes = [f'{i}) {recipe_name}' for i, recipe_name in enumerate(
        shopping_cart.values_list("recipe__name", flat=True), 1
    )]

    return '\n'.join([
        'Карта покупок.',
        '',
        'Необходимо купить:',
        *ingredients,
        '',
        'Для приготовления рецептов:',
        *recipes,
        '',
        f'Дата создания карты покупок: {time_now}.'
    ])
