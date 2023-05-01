docker rm -f $(docker ps -q)

git reset --hard HEAD

git pull

chmod +x start.sh
chmod +x stop.sh
chmod +x update.sh

docker-compose --env-file config/config.env up --build --detach