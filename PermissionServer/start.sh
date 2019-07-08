./vnc_startup.sh

uwsgi --http-socket :9090 --plugin python3 --wsgi-file ./src/wsgi.py