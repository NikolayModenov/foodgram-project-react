# Foodgram.

![foodgram workflow](https://github.com/NikolayModenov/foodgram-project-react/actions/workflows/main.yml/badge.svg)

### Автор

1. Николай Моденов  
   - Аккаунт GitHub: [NikolayModenov](https://github.com/NikolayModenov)

## Описание

Проект foodgram представляет собой платформу на которой каждый может поделиться своим рецептом, просматривать рецепты других пользователей, подписаться под разными авторами и разными рецептами, создать список покупок продуктов тех рецептов которые заинтересовали.

Просматривать рецепты и страницы пользователей могут любые посетители. 

Подписываться на рецепты и авторов, а так же добавлять свои рецепты могут только зарегистрированные посетители.

docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py loaddata data/tags.json
docker compose exec backend python manage.py loaddata data/ingredients.json