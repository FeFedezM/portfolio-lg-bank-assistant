FROM python:3.11-slim

WORKDIR /app

COPY ./app .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD [ "uvicorn" , "main:app", "--reload","--host", "0.0.0.0", "--port", "80"]
