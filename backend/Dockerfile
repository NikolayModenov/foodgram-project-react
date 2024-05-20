FROM python:3.9

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic

CMD ["gunicorn", "--bind", "0.0.0.0:9009", "backend.wsgi"]
