./vnc_startup.sh

npm run start --silent -- --no-sandbox
uwsgi --http-socket :9090 --plugin python3 --wsgi-file ./src/wsgi.py --set is_aws=False --set db_hostname=db --set db_port=3306 --set db_user=root --set db_password=supersecret
