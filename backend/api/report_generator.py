from django.utils import timezone, dateformat


def format_shopping_cart_report(shopping_cart):
    '''Format the shopping list into text for download.'''

    time_now = dateformat.format(
        timezone.localtime(timezone.now()), 'Y-m-d H:i:s'
    )
    for cart in shopping_cart:
        print(f'cart = {cart}')

    return '\n'.join([
        'Карта покупок.',
        '',
        'Необходимо купить:',
        *[
            f'{i}) {ingredient["name"].capitalize()} = {ingredient["amount"]} '
            f'{ingredient["unit"]}.'
            for i, ingredient in enumerate(shopping_cart, 1)
        ],
        '',
        'Для приготовления рецептов:',
        *[f'{i}) {recipe_name}' for i, recipe_name in enumerate(
            set(shopping_cart.values_list("recipe__name", flat=True)), 1
        )],
        '',
        f'Дата создания карты покупок: {time_now}.'
    ])
