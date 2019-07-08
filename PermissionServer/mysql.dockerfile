FROM mysql

ENV MYSQL_DATABASE streamingOS

COPY ./sql-scripts/ /docker-entrypoint-initdb.d/

#docker run -d -p 3306:3306 --net mynet --name db -e MYSQL_ROOT_PASSWORD=supersecret mysql-db:latest
#docker build -t mysql -f mysql.dockerfile .
