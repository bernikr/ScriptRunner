FROM python:3.8

COPY . /

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
VOLUME /scripts
ENV SCRIPT_DIR="/scripts"

CMD [ "uwsgi",  "--ini", "uwsgi.ini" ]
