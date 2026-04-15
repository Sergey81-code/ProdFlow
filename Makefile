DC = docker compose
APP_LOCAL_FILE = docker-compose.yaml
APP_CI_FILE = docker-compose.yaml



up:
	${DC} -f ${APP_LOCAL_FILE} up -d
down:
	${DC} -f ${APP_LOCAL_FILE} down && docker network prune --force
up_rebuild:
	${DC} -f ${APP_CI_FILE} up --build -d
