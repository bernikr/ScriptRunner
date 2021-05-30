gunicorn -k flask_sockets.worker -w 8 -b :8000 main:app --max-requests 100 --timeout 60 --keep-alive 60
