
PREFIX                  ?= $(shell pwd)
VERSION                 ?= $(shell cat VERSION)

all:  install build

install:
	@echo ">> installing dependencies"
	@pip install -r requirements.txt.lock -i https://mirrors.aliyun.com/pypi/simple/

build:
	@echo ">> building package with docker"
	@sudo rm -rf release
	@mkdir release
	@time docker-compose up --build
	@sync
	@echo ">> building package done"
	@echo ">> building package done"
	@echo ">> building package done"
