#include<stdio.h> 
#include<stdlib.h>
#include<sys/wait.h> 
#include<unistd.h> 

char* int2string(int);


int main(int argc, char* argv[]) { 
  int children_pids[2];									// process id's for children for parent promgram to wait for them to finish before terminating
  children_pids[0] = fork();							// making a child process that will copy our memory and continue from this point in the program
  if(children_pids[0] == 0){								//fork returns process id of the newly made child to the parent and 0 to the child, thus we are checking if we are the child here
	  char* argv[] = {"ChildFifoTest", "Reader", NULL}; // setting up argv array for the new process
	  
	  execv(argv[0],argv);								// switching this process to run the program specified by argv[0]
  }
  else{
	children_pids[1] = fork();							// making a child process that will copy our memory and continue from this point in the program
	if(children_pids[1] == 0){								//fork returns process id of the newly made child to the parent and 0 to the child, thus we are checking if we are the child here
		char* argv[] = {"ChildFifoTest","Writer", NULL};// setting up argv array for the new process
		execv(argv[0],argv);							// switching this process to run the program specified by argv[0]
	}
	else{
		int i = 0;
		for(i =0; i<2; i++){
			waitpid(children_pids[i], NULL, 0);			//waiting on child to finish before we exit
		}
	}	  
	  
  }
  
  return 0;
} 

/*USELESS FUNCTION NOW
char * int2string(int number){							//function to turn an integer to a string. Was using during testing to track children and parent process id's between programs.
	char * string = malloc(501);
	int pos = 0;

	do{
		if(pos >500){
			return NULL;
		}
		string[pos] = (number%10) + '0';
		number /= 10;
		pos++;
	}while(number>0);
	
	string[pos] = 0;
	
	int i,j;
	char temp = 0;
	for(i=0, j=pos-1; i<pos/2; i++, j--){
		temp = string[i];
		string[i] = string[j];
		string[j] = temp;
	}
	
	return string;
}
*/