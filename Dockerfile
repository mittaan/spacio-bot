FROM python:3.12.7

WORKDIR /usr/app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "./src/main.py"]