1. Build the docker image from the dockerfile
docker build -t os .
(Add --no-cache to rebuild from scratch dependencies)

2. Make sure the DB is running
(In a seperate terminal) (Refer to Reverse Proxy code for instruction)

3. docker run --cap-add=NET_ADMIN --name os -v "$(pwd)/src:/dockerstartup/src/" --net mynet os:latest
