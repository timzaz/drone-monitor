FROM python:3.8

ENV PYTHONUNBUFFERED 1
ENV GEVENT_SUPPORT=True
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000

COPY . .
CMD flask run --host 0.0.0.0 --port 5000
