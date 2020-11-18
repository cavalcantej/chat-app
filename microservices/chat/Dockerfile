FROM python:3.8.6-alpine

WORKDIR /project
ADD . .

RUN pip install -r requirements.txt
CMD ["python", "app.py"]