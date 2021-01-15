FROM python:3.8

COPY . /

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
VOLUME /scripts
ENV SCRIPT_DIR="/scripts"

CMD [ "gunicorn", "main:app", "-b", ":8000", "-k", "gevent" ]
