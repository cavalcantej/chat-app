FROM python:3.8



WORKDIR /app
ADD . .
# RUN apk add --no-cache python3-dev libffi-dev gcc musl-dev make
RUN pip install -r requirements.txt

EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["app.py"]