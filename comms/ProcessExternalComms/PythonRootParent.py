import os

if len(os.sys.argv) != 2:
    print("Improper Command line arguments provided")
    print("Call promgram with 'python3 PythonRootParent.py name_of_new_process_to_start'")
    exit()

child_pid = os.fork() #linxu sys call to create a copy child process of yourself

if(child_pid ==0):
		#os.execv(argv[0],argv)
		os.system('python3 ' + os.sys.argv[1] +  ' Writer')#Same as writing a command in the terminal to start a python program


else:
	child_pid = os.fork()

	if(child_pid ==0):
		#os.execv(argv[0],argv)
		os.system('python3 ' + os.sys.argv[1] +  ' Reader') #Same as writing a command in the terminal to start a python program

exit()
