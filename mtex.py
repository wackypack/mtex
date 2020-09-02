 ############################################# 
#                                             #
#                                             #
#         Tone Extractor for Python 3         #
#                                             #
#    Rev 4b: Fixed IMY exporting;             #
#              added MLD support.             #
#                                             #
#                                             #
#             Currently supports:             #
#                                             #
#         • DXM: Feelsound DXM files          #
#         • IMY: iMelody ringtones            #
#         • MFM: Panasonic MFM files          #
#         • MID: MIDI files                   #
#         • MLD: Melody ringtones             #
#         • MMF: SMAF ringtones               #
#         • PMD: AU-PMD ringtones             #
#                                             #
 ############################################# 

import tkinter as tk
from tkinter import filedialog
import os
from os.path import dirname, basename, splitext, join

root = tk.Tk()
root.withdraw()

filePath=filedialog.askopenfilename()
file=open(filePath,mode='rb')
size=os.path.getsize(filePath)
outDir=dirname(filePath)
BaseName=splitext(basename(filePath))[0]

Bin=file.read()

outFile=input("Please give a name prefix for output files: ")
numFiles=0

sr=iter(range(size))

# File identifiers vv

dxmHeader = b"MCDF"
dxmEof = b"\xFF\x2F\x00"
midiHeader = b"MThd"
midiFalseEof = b'\xff/\x00MTrk'
midiEof = b"\xFF\x2F\x00"
pmdHeader = b"cmid"
pmdFalseEof = b"\xFF\xDF\x00trac"
pmdEof = b"\xFF\xDF\x00"
mldHeader = b"melo"
mfmHeader = b"mfmp"
mfmFalseEof = b"\xFF\xB1\x00trac"
mfmEof = b"\xFF\xB1\x00"
mmfHeader = b"MMMD"
imyHeader = b"BEGIN:IMELODY"
imyEof = b"END:IMELODY"
mxmfHeader = b"XMF_2.00"

# File identifiers ^^


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
    # Pick up iMelody files.
    if Bin[x:x+1] == b"B":
        chunkSize=0
        if Bin[x:x+13] == imyHeader:
            readByte=Bin[x+chunkSize:x+chunkSize+11]
            while readByte != imyEof:
                chunkSize+=1
                readByte=Bin[x+chunkSize:x+chunkSize+11]
                if chunkSize >= size-x:
                    readByte=imyEof
            if readByte == imyEof:
                writeFile(x, chunkSize+11, "imy")
    # Pick up PMD files.
    if Bin[x:x+1] == b"c":
        chunkSize=0
        if Bin[x:x+4] == pmdHeader:
            check=""
            test=False
            while test == False:
                chunkSize+=1
                readByte=Bin[x+chunkSize:x+chunkSize+3]
                if readByte == pmdEof:
                    try:
                        check=Bin[x+chunkSize:x+chunkSize+7]
                        if check == pmdFalseEof:
                            test=False
                        else:
                            test=True
                    except:
                        chunkSize+=4
                        test=True
                if chunkSize >= size-x:
                    test=True
            if test == True:
                writeFile(x, chunkSize+3, "pmd")
                    
    # Pick up MFM or MLD files.
    if Bin[x:x+1] == b"m":
        chunkSize=0
        # Check for MFM file.
        if Bin[x:x+4] == mfmHeader:
            check=""
            test=False
            while test == False:
                chunkSize+=1
                readByte=Bin[x+chunkSize:x+chunkSize+3]
                if readByte == mfmEof:
                    try:
                        check=Bin[x+chunkSize:x+chunkSize+7]
                        if check == mfmFalseEof:
                            test=False
                        else:
                            test=True
                    except:
                        chunkSize+=4
                        test=True
                if chunkSize >= size-x:
                    test=True
            if test == True:
                writeFile(x, chunkSize+3, "mfm")
        # Check for MLD file.
        if Bin[x:x+4] == mldHeader:
            check=""
            test=False
            while test == False:
                chunkSize+=1
                readByte=Bin[x+chunkSize:x+chunkSize+3]
                if readByte == pmdEof:
                    try:
                        check=Bin[x+chunkSize:x+chunkSize+7]
                        if check == pmdFalseEof:
                            test=False
                        else:
                            test=True
                    except:
                        chunkSize+=4
                        test=True
                if chunkSize >= size-x:
                    test=True
            if test == True:
                writeFile(x, chunkSize+3, "mld")
                    
    # Pick up DXM, MMF, or MIDI files; headers starting with "M".
    if Bin[x:x+1] == b"M":
        chunkSize=0
        # Check for DXM file.
        if Bin[x:x+4] == dxmHeader:
            readByte=0
            while readByte != dxmEof:
                chunkSize+=1
                readByte=Bin[x+chunkSize:x+chunkSize+3]
                if chunkSize >= size-x:
                    readByte=dxmEof
            if readByte == dxmEof:
                writeFile(x, chunkSize+3, "dxm")
                
        # Check for MMF file.
        if Bin[x:x+4] == mmfHeader:
            chunkSize=int.from_bytes(Bin[x+4:x+8], "big")
            writeFile(x, chunkSize+8, "mmf")
        
        # Check for MIDI file.
        if Bin[x:x+4] == midiHeader:
            check=""
            test=False
            while test == False:
                chunkSize+=1
                readByte=Bin[x+chunkSize:x+chunkSize+3]
                if readByte == midiEof:
                    try:
                        check=Bin[x+chunkSize:x+chunkSize+7]
                        if check == midiFalseEof:
                            test=False
                        else:
                            test=True
                    except:
                        chunkSize+=4
                        test=True
                if chunkSize >= size-x:
                    test=True
            if test == True:
                writeFile(x, chunkSize+3, "mid")


print("Found %s total hits." % str(numFiles))
input("Press Enter to exit")
