@echo off
if ("%~1"=="") (python tonesniffer.py) else (python %~dp0\tonesniffer.py %1)