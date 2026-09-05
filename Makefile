CFLAGS := -O3 -Wall -Iincludes -Llib -lraylib

ifeq ($(OS),Windows_NT)
	CFLAGS += -lwinmm -lgdi32
endif

blinky: 
	g++ blinky.cxx $(CFLAGS) -o blinky.exe
