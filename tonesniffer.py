 ############################################# 
#                                             #
#                                             #
#          ToneSniffer for Python 3           #
#                   v2.1                      #
#                                             #
#                                             #
#             Currently supports:             #
#                                             #
#         • DLS: Downloadable Sounds          #
#         • DXM: Feelsound DXM files          #
#         • IMY: iMelody ringtones            #
#         • MFM: Faith MFM files              #
#         • MID: MIDI files                   #
#         • MLD: MLD ringtones                #
#         • MMF: SMAF ringtones               #
#         • NRT: Nokia ringtones              #
#         • PMD: AU-PMD ringtones             #
#         • QCP: Qualcomm audio container     #
#         • RMI: RIFF MIDI                    #
#         • SF2: SoundFont banks              #
#         • WAV: RIFF Wave                    #
#                                             #
 #############################################




import tkinter as tk
import sys
from tkinter import filedialog
import os
from os.path import dirname, basename, splitext

root = tk.Tk()
root.withdraw()

def findPrompt(msg):
    msgPrompt=input("%s (y/n) " % msg)
    if msgPrompt.lower() == "y":
        return True
    elif msgPrompt.lower() == "n":
        return False
    while msgPrompt.lower() not in ("y", "n"):
        msgPrompt=input("%s (type \'y\' or \'n\' - without quotes) " % msg)
        if msgPrompt.lower() == "y":
            return True
        elif msgPrompt.lower() == "n":
            return False

if len(sys.argv)==2:
    filePath=sys.argv[1]
else:
    filePath=filedialog.askopenfilename()

file=open(filePath,mode='rb')
size=os.path.getsize(filePath)
outDir=dirname(filePath)
BaseName=splitext(basename(filePath))[0]

Bin=file.read()

outFile=input("Enter a name prefix for output files: ")

findMmf=True
findImy=False
findMld=False
findNrt=False

findMmf=findPrompt("Look for SMAF files?        ")
findImy=findPrompt("Look for iMelody files?     ")
findMld=findPrompt("Look for Faith mld files?   ")
findNrt=findPrompt("Look for Nokia mono ringers?")
    
numFiles=0

sr=iter(range(size))


# Functions vv

def writeFile(address, size, ext):
    global numFiles
    outBytes=Bin[address:address+size]
    output=open(outDir+"/%s_%s.%s" % (outFile, str(numFiles), ext), mode="xb")
    output.write(outBytes)
    output.close()
    print("Exported %s_%s.%s at address %s, size %s" % (outFile, str(numFiles), ext, hex(address), str(size)))
    numFiles+=1

# Functions ^^


print("Now searching "+basename(filePath))

for x in sr:
    if Bin[x:x+3] in [b"MTh", b"MCD", b"cmi", b"mel", b"mfm", b"MMM", b"RIF", b"BEG", b"\x00\x0A\x08", b"\x00\x02\xFC"]:
        chunkSize=0
        if Bin[x:x+4] == b"MThd" and Bin[x+14:x+18] == b"MTrk":
            check=""
            test=False
            mtrkSize=int.from_bytes(Bin[x+18:x+22], "big")
            chunkSize=mtrkSize+22
            while not test:
                if Bin[x+chunkSize:x+4+chunkSize] == b"MTrk":
                    mtrkSize=int.from_bytes(Bin[x+chunkSize+4:x+chunkSize+8], "big")
                    chunkSize+=mtrkSize+8
                if Bin[x+chunkSize:x+4+chunkSize] != b"MTrk":
                    test=True
            if test:
                writeFile(x, chunkSize, "mid")

        if Bin[x:x+4] == b"MCDF":
            readByte=0
            while readByte != b"CTrk":
                chunkSize+=1
                readByte=Bin[x+chunkSize:x+chunkSize+4]
                if chunkSize >= size-x:
                    break
            if readByte == b"CTrk":
                trkLen=int.from_bytes(Bin[x+chunkSize+4:x+chunkSize+8], "big")
                chunkSize+=trkLen+8
                writeFile(x, chunkSize, "dxm")

        if Bin[x:x+4] == b"cmid":
            chunkSize=int.from_bytes(Bin[x+4:x+8], "big")
            if chunkSize >= 16 and chunkSize <= 1048576:
                writeFile(x, chunkSize+8, "pmd")
			
        if findMld and Bin[x:x+4] == b"melo":
            chunkSize=int.from_bytes(Bin[x+4:x+8], "big")
            if chunkSize >= 16 and chunkSize <= 1048576:
                writeFile(x, chunkSize+8, "mld")

        if Bin[x:x+4] == b"mfmp":
            chunkSize=int.from_bytes(Bin[x+4:x+8], "big")
            if chunkSize >= 16 and chunkSize <= 1048576:
                writeFile(x, chunkSize+8, "mfm")

        if findMmf and Bin[x:x+4] == b"MMMD":
            chunkSize=int.from_bytes(Bin[x+4:x+8], "big")
            if chunkSize >= 16 and chunkSize <= 1048576:
                writeFile(x, chunkSize+8, "mmf")

        if Bin[x:x+4] == b"RIFF":
            chunkSize=int.from_bytes(Bin[x+4:x+8], "little")
            if chunkSize >= 16:
                if Bin[x+8:x+12] == b"WAVE":
                    writeFile(x, chunkSize+8, "wav")
                if Bin[x+8:x+12] == b"DLS ":
                    writeFile(x, chunkSize+8, "dls")
                if Bin[x+8:x+12] == b"sfbk":
                    writeFile(x, chunkSize+8, "sf2")
                if Bin[x+8:x+12] == b"RMID":
                    writeFile(x, chunkSize+8, "rmi")
                if Bin[x+8:x+12] == b"QLCM":
                    writeFile(x, chunkSize+8, "qcp")

        if Bin[x:x+13] == b"BEGIN:IMELODY":
            readByte=Bin[x+chunkSize:x+chunkSize+11]
            while readByte != b"END:IMELODY":
                chunkSize+=1
                readByte=Bin[x+chunkSize:x+chunkSize+11]
                if chunkSize >= size-x or chunkSize >= 16384:
                    break
            if readByte == b"END:IMELODY":
                writeFile(x, chunkSize+11, "imy")

        if findNrt and Bin[x:x+3] == b"\x00\x0A\x08":
            readByte=0
            while readByte != b"\x07\x0B":
                chunkSize+=1
                readByte=Bin[x+chunkSize:x+chunkSize+2]
                if chunkSize >= size-x:
                    readByte=b"\x07\x0B"
            if readByte == b"\x07\x0B":
                writeFile(x, chunkSize+2, "nrt")

        if findNrt and Bin[x:x+3] == b"\x00\x02\xFC":
            readByte=0
            while readByte != b"\x07\x0B":
                chunkSize+=1
                readByte=Bin[x+chunkSize:x+chunkSize+2]
                if chunkSize >= size-x:
                    readByte=b"\x07\x0B"
            if readByte == b"\x07\x0B":
                writeFile(x, chunkSize+2, "nrt")

print("Found %s total hits." % str(numFiles))
input("Press Enter to exit")
