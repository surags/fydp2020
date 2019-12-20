import peewee
import uwsgi

# Create a database instance that will manage the connection and
# execute queries
db = peewee.MySQLDatabase(
    "streamingOS",
    host=uwsgi.opt["db_hostname"].decode("utf-8"),
    port=int(uwsgi.opt["db_port"].decode("utf-8")),
    user=uwsgi.opt["db_user"].decode("utf-8"),
    passwd=uwsgi.opt["db_password"].decode("utf-8")
)


class BaseModel(peewee.Model):
    class Meta:
        database = db



