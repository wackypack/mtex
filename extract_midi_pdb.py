 ############################################# 
#                                             #
#                                             #
#             Treo Tone Extractor             #
#                for Python 3                 #
#                                             #
#                                             #
 #############################################

import tkinter as tk
from tkinter import filedialog
import os
from os.path import dirname, basename, splitext, isfile, isdir, join

root = tk.Tk()
root.withdraw()

filePath=filedialog.askopenfilename()
file=open(filePath,mode='rb')
size=os.path.getsize(filePath)
BaseName=splitext(basename(filePath))[0]
outDir=join(dirname(filePath), BaseName)
if not os.path.isdir(outDir):
    os.mkdir(outDir)

Bin=file.read()
numFiles=0
sr=iter(range(size))

# Functions vv

def writeFile(address, size, name):
    global numFiles
    outBytes=Bin[address:address+size]
    if isfile(outDir+"/%s.mid" % name):
        suffix=2
        while isfile(outDir+"/%s (%s).mid" % (name, str(suffix))):
            suffix+=1
        output=open(outDir+"/%s (%s).mid" % (name, str(suffix)), mode="xb")
    else:
        output=open(outDir+"/%s.mid" % name, mode="xb")
    output.write(outBytes)
    output.close()
    print("Exported %s.mid at address %s, size %s" % (name, hex(address), str(size)))
    numFiles+=1

# Functions ^^

print("Now searching "+BaseName)

for x in sr:
    if Bin[x:x+1] == b"P":
        # Pick up Palm MIDI resource.
        if Bin[x:x+4] == b"PMrc":
            HeadLen=int.from_bytes(Bin[x+4:x+6], "little")
            NameLen=HeadLen-7
            OutName=str(Bin[x+6:x+6+NameLen], "utf-8")
            MidBegin=x+HeadLen
            MidLen=0
            check=""
            complete=False
            while complete == False:
                MidLen+=1
                readByte=Bin[MidBegin+MidLen:MidBegin+MidLen+3]
                if readByte == b"\xFF\x2F\x00":
                    try:
                        check=Bin[MidBegin+MidLen:MidBegin+MidLen+7]
                        if check == b"\xFF\x2F\x00MTrk":
                            complete=False
                        else:
                            complete=True
                    except:
                        MidLen+=4
                        complete=True
                if MidLen >= size-MidBegin:
                    complete=True
            if complete == True:
                writeFile(MidBegin, MidLen+3, OutName)

print("Found %s total hits." % str(numFiles))
input("Press Enter to exit")
