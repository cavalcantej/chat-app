FROM python:3.8.6-alpine

WORKDIR /monolithic
ADD . /monolithic

RUN pip install -r requirements.txt
RUN pip install 'pymongo[srv]' dnspython
CMD ["python", "app.py"]