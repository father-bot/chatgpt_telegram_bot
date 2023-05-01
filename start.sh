export GIT_PYTHON_GIT_EXECUTABLE=$(whereis git | awk '{print $2}')

docker-compose --env-file config/config.env up --build --detach