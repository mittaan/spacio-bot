FROM python:3.12-alpine

WORKDIR /usr

COPY requirements.txt .

USER root
RUN adduser --system --no-create-home bombolo
RUN pip install -r requirements.txt

COPY . .

WORKDIR /usr/src
RUN chown -R bombolo ./logs

USER bombolo
CMD ["python", "main.py"]