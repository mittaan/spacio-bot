FROM python:latest

COPY src /

RUN pip install -r requirements.txt

CMD ["python", "./src/main.py"]