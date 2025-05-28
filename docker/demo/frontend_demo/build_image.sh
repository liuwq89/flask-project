IMAGE_NAME="frontend_server"
TIMENOW=$(date +%y.%m.%d.%H%M)

# docker_name="${IMAGE_NAME}:${MODE}_${COMMIT_ID}_${TIMENOW}"
docker_name="${IMAGE_NAME}:${TIMENOW}"

docker build -t ${docker_name} .

dist_bak_name="dist.${TIMENOW}"
mv ./dist ${dist_bak_name}





