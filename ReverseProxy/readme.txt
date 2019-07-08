For the first time (or making DB changes)

1. Build and run the database
docker build -t mysql -f mysql.dockerfile .
docker run -d -p 3306:3306 --net mynet --name db -e MYSQL_ROOT_PASSWORD=supersecret mysql:latest
docker start db

2. Build and run the server
docker build -t rp .
docker run --cap-add=NET_ADMIN -v "$(pwd):/usr/src/app/" --net mynet -p9090:9090 -p8080-8085:8080-8085 --name rp rp:latest

// When you change the server code
docker stop rp
docker start rp


3. Log into the database (if you need to)
docker exec -it db bash
mysql -uroot -psupersecret
use streamingOS;

// Add this data into it if there's a foreign key issue
INSERT INTO usertype (user_type) VALUES ('student');
INSERT INTO usertype (user_type) VALUES ('teacher');


For not the first time:
docker start db
docker start rp


Useful commands:

docker-machine ls
// To determine the URL to hit (should be something like this: tcp://192.168.99.100:2376)
// In Postman, hit rest calls like GET 192.168.99.100:9090/test (IMPORTANT: Change the port to 9090)

docker ps
// To determine which containers are currently active

docker stop rp
// To kill the container called rp

docker rm rp
// To remove the container called rp

docker logs rp -f --tail 20
// To view the logs of rp for the last 20 lines

