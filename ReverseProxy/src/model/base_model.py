import peewee

# Create a database instance that will manage the connection and
# execute queries
db = peewee.MySQLDatabase(
    "streamingOS",
    host="db",
    port=3306,
    user="root",
    passwd="supersecret"
)

class BaseModel(peewee.Model):
    class Meta:
        database = db



