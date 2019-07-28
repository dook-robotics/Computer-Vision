# ------------- #
# Mikian Musser #
# 07/27/2019    #
# ------------- #

# @usage python replace.py {dir}
# @uexmp python replace.py {D:/Computer-Vision/cardcv/images/test/}

import fileinput
import sys
import os
import re

# 'D:/Computer-Vision/cardcv/images/test/'
# 'D:/Computer-Vision/cardcv/images/train/'

filepath = str(sys.argv[1])
text_to_search = ["king", "queen", "jack", "ten", "nine", "ace"]
replacement_text = 'card'

count = 0

filename = ''
for filedir in os.listdir(filepath):
    if filedir.endswith(".jpg") or filedir.endswith(".JPG"):
        filename = filedir
        filename = filename.replace(".jpg", ".xml").replace(".JPG", ".xml")
        with fileinput.FileInput(filepath + filename, inplace=True, backup='.bak') as file:
            for line in file:
                line = re.sub('(king|queen|jack|ten|nine|ace)', 'card', line)
                print(line, end='')
        os.remove(filepath + filename + '.bak')
        count = count + 1

print(count, "Files Updated")
