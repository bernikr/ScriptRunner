FROM python:3.8

COPY . /

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
VOLUME /scripts
ENV SCRIPT_DIR="/scripts"

CMD gunicorn --worker-class gevent --workers 8 --bind :8000 main:app --max-requests 100 --timeout 60 --keep-alive 60
