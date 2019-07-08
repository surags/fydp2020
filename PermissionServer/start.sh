source environment_variables.sh
uwsgi --http-socket :9090 --plugin /usr/lib/uwsgi/python3_plugin.so --wsgi-file src/wsgi.py