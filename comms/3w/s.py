import os

os.system('rm 000001')
os.system('rm 000010')
os.system('rm 001000')
os.system('rm 010000')
print("Removed fifos")
os.system('mkfifo 000001')
os.system('mkfifo 000010')
os.system('mkfifo 001000')
os.system('mkfifo 010000')
print("Remade fifos")
