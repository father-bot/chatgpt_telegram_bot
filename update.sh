docker rm -f $(docker ps -q)

git pull

docker-compose --env-file config/config.env up --build --detach