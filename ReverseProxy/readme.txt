1. Build the docker image from the dockerfile
docker build -t rp . 
(Add --no-cache for dependencies)

2. docker build db
(In a seperate terminal)

3. Run the docker container as follows:
docker run --cap-add=NET_ADMIN --net mynet -p9090:9090 -p8080-8085:8080-8085 --name rp rp:latest
(docker rm rp) to remove
(docker stop rp) to kill it

(If you want to run rp and launch the shell in the container):
// docker run --cap-add=NET_ADMIN --net mynet -it -p9090:9090 -p8080-8085:8080-8085 --name rp rp:latest /bin/ash

4. Navigate to localhost:9090 and you should be met with "hello world"
(To get the IP, run docker-machine ls)