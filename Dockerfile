FROM arm32v7/python:3

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

EXPOSE 80

COPY ./src /app

CMD ["uvicorn", "app.nemo.main:app", "--host", "0.0.0.0", "--port", "80"]