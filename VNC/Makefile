cc = gcc
libs= -lvncclient -lSDL2 -lz -ljpeg -lpthread
all: client client-debug

client: SDLvncviewer.c
	${cc} SDLvncviewer.c -o client ${libs}

client-debug: SDLvncviewer.c
	${cc} SDLvncviewer.c -o client-debug ${libs} -g

clean:
	rm client client-debug
