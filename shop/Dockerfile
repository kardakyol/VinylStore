FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT=8080

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN mkdir -p /vol/web/static

RUN python manage.py collectstatic --noinput --clear || true

EXPOSE 8080

CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:$PORT"]

