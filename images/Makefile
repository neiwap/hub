DOCKERFILES=$(wildcard */Dockerfile)
_IMAGES=$(dir $(DOCKERFILES))
IMAGES=$(_IMAGES:%/=%.img)

all:$(IMAGES)

%.img:$(wildcard %/*)
	docker build -t $(@:%.img=%) $(@:%.img=%)


