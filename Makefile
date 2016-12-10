all: build test
build:
	docker build -t jbonachera/nsmaster . 
test:
	cd tests/ && tox
