# https://just.systems

# docker compose use local compose yaml
dcl *args:
  docker compose -f docker-compose.local.yaml {{args}}