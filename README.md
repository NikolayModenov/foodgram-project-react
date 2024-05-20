# praktikum_new_diplom
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py loaddata data/tags.json
docker compose exec backend python manage.py loaddata data/ingredients.json