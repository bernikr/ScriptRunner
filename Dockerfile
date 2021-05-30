FROM python:3.9
EXPOSE 8000
VOLUME /scripts
ENV SCRIPT_DIR="/scripts"

COPY requirements.txt /

RUN pip install -r requirements.txt

COPY . /

CMD gunicorn -k flask_sockets.worker --bind :8000 main:app
