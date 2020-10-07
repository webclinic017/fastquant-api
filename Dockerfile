FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./app /app
WORKDIR /app
RUN pip install -r requirements.txt

WORKDIR /
ENTRYPOINT [ "python", "/app/app.py" ]