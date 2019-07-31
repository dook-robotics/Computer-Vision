
CC = gcc

all: RootParent ChildFifoTest fifo

RootParent: RootParent.c
	$(CC) -o $@ $<
	
ChildFifoTest: ChildFifoTest.c
	$(CC) -o $@ $<
	
fifo:
	mkfifo "ReadWriteBuffer";
	
clean:
	rm "ReadWriteBuffer";