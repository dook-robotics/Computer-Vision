/*Do not call this program on its own. This program is a test to show that a parent process can start
 two new process and also test that those processes can have a channel of communication between them
 namely the fifo 'ReadWriteBuffer' use the program RootParent*/
/*The FIFO must be made outside of this program. This program is only testing that the FIFO system works, it is not automatically creating FIFOs*/

#include<stdio.h> 
#include<unistd.h>
#include<fcntl.h>
#include<unistd.h> 
#include<string.h>
#include<stdbool.h>

void writer();
void reader();

int main(int argc, char* argv[]) { 
  if(strcmp(argv[1],"Reader") == 0){			//if we are a reader, call the reader routine
	  reader();
  }
  else if(strcmp(argv[1],"Writer") == 0){		//if we are a writer call the writer routine
	  writer();
  }
  else{											//otherwise, Program called incorrectly
	printf("argv[1] was not set properly:  %s\n", argv[1]);  
  }
  
  return 0;
} 

void writer(){
	int i = 0;
	sleep(5);									//writer will sleep for 5 seconds to show that the reader can chekc the file and continue working and check it agian later
	int fd = open("ReadWriteBuffer", O_WRONLY);	//open a file (fifo) and return int file descriptor
	if(fd <0){									//make sure file opened properly
		printf("fifo did not open properly\n");
	}
	char buffer[] ="Hello World!";				//string to write to file
	printf("Writing Now\n");
	int bytes = write(fd, buffer, sizeof(buffer));//write buffer to file and receive back how many bytes were written, if bytes return <0 -> error occurred
	if (bytes < 0) {
		printf("Error Writing to file\n");
	}

	close(fd);
}

void reader(){
	int bytes;
	int fd = open("ReadWriteBuffer", O_RDONLY | O_NONBLOCK);//open a file (fifo) and return int file descriptor, this file will be NON_BLOCKING (If the file is empty when we read from it we will not sit around and wait for data to be written)
	char buffer[100];
	int i=0;
	if(fd <0){
		printf("fifo did not open properly\n");				//make sure file opened properly
	}
	
	
	for(i=0; i<100; i++){ //make sure buffer is cleaned up before use
		buffer[i] =0;
	}
	i =0;
	bool doneRead = false;
	bool readSomething = false;
	while(!doneRead){
		bytes = read(fd, buffer+i, 1);
		if(buffer[i] == 0 && readSomething){									//if we read the NULL character, we are done reading
			doneRead = true;
		}
		if(bytes <= 0 && readSomething == true){										//if we read nothing from the file, then the file is now empty, we are done reading
			doneRead = true;
		}
		else if (bytes <= 0 && readSomething == false) {
			printf("File still empty\n");
			sleep(1);										//simulating that the reader is doing other work before it goes and checks if the file again for data entires
			continue;
		}
		if(i>= 100){										//make sure to correct buffer overflow if more than 100 bytes have been written to the file
			i = 100;
			buffer[i] = 0;
		}
		else{
			readSomething = true;
			i++;
		}
		
	}
	
	
	if(buffer[0] > 0){										//We read something, so print it
		printf("We read the file correctly\nWe read \'%s\'\n", buffer);
	}
	else if(buffer[i] == 0){
		printf("We did not read anything but did not get stuck waiting\n");
	}
	else{
		printf("Read error\n");
	}
	
	close(fd);
}
