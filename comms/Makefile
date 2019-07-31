SHELL := /bin/bash
CC := gcc
CFLAGS := -g -O2 -Wall -pthread


.PHONY: all clean fifos 

all: oshow patrons

oshow: oshow.c
	$(CC) -o $@ $(CFLAGS) $<

patrons: patrons.c
	$(CC) -o $@ $(CFLAGS) $<

clean:
	@rm -f *.o oshow patrons

fifos:
	for (( i=0; i <10; i++)) do \
	    mkfifo "kiosk-client$$i";\
	    mkfifo "kiosk-server$$i";\
	done

.SUFFIXES: .c .o .obj .dmp 

