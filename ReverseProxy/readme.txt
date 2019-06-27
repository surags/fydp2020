1. Build the docker image from the dockerfile
docker build -t rp .

2. Run the docker container as follows:
docker run -p9090:9090 --name rp rp:latest

3. Navigate to localhost:9090 and you should be met with "hello world" 