# project basics
project_name = PinewoodDerby
project_root = ~/Projects/${project_name}

backend_root = ${project_root}

# virtual env & paths to executables
venv_dir = ~/.pyenv/versions/${project_name}
python = ${venv_dir}/bin/python

# docker settings
docker_registry = docker.io
docker_user = cubpack645
docker_image = pinewoodderby

all:
	@echo "please specify a make target, as no default is set"

reqs:
	cd ${backend_root} && pip-compile
	cd ${backend_root} && pip install -r requirements.txt

docker_build:
	@echo "building docker file"
	docker-compose -f docker-compose.yml build

docker_push:
	@echo "pushing docker image"
	docker login ${docker_registry}
	docker image tag ${docker_image} ${docker_user}/${docker_image}
	docker push ${docker_user}/${docker_image}
