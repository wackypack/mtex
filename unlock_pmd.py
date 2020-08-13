

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from os import listdir
from os.path import dirname, basename, isfile, isdir, join
import shutil

root = tk.Tk()
root.withdraw()

messagebox.showinfo("", "Navigate to directory of PMD files.")
filePath=filedialog.askdirectory()
if not filePath:
    print("File dialog cancelled")
    exit()

dirFiles = [d for d in listdir(filePath) if isfile(join(filePath, d))]
pmdFiles = [f for f in dirFiles if f[-4:]==".pmd"]

outPath=filePath+"/Unlocked"
if not os.path.isdir(outPath):
    os.mkdir(outPath)

for t in pmdFiles:
    file=open(join(filePath,t), "rb")
    size=os.path.getsize(join(filePath,t))
    for x in range(size):
        reader=""
        sorcPos=0
        fail=False
        while reader != b"sorc":
            file.seek(sorcPos)
            reader = file.read(4)
            sorcPos+=1
            if sorcPos >= size:
                print("File %s is not a valid PMD file" % t)
                file.close()
                fail=True
                break 
        if reader == b"sorc":
            file.seek(sorcPos+3)
            check=file.read(3)
            if check == b"\x00\x01\x00":
                print("File %s is not copy-protected" % t)
                file.close()
            else:
                shutil.copyfile(join(filePath,t), join(outPath,t))
                outFile=open(join(outPath,t), "r+b")
                outFile.seek(sorcPos+3)
                outFile.write(b"\x00\x01\x00")
                print("Copy protection removed on file %s" % t)
                file.close()
                outFile.close()
            break
        if fail:
            break
input("Done. Press enter to close")
