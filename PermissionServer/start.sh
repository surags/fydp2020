./vnc_startup.sh

npm start --silent
uwsgi --http-socket :9090 --plugin python3 --wsgi-file ./src/wsgi.py
