1. Build the docker image from the dockerfile
docker build -t rp .

2. Run the docker container as follows:
docker run --cap-add=NET_ADMIN --net mynet -p9090:9090 --name rp rp:latest

(If you want to run rp and launch the shell in the container):
// docker run --cap-add=NET_ADMIN --net mynet -it -p9090:9090 --name rp rp:latest /bin/ash

3. Navigate to localhost:9090 and you should be met with "hello world" 