./vnc_startup.sh

npm run start --silent -- --no-sandbox
uwsgi --http-socket :9090 --plugin python3 --wsgi-file ./src/wsgi.py
