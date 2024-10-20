FROM python:3.12-alpine

WORKDIR /usr

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

WORKDIR /usr/src

CMD ["python", "main.py"]