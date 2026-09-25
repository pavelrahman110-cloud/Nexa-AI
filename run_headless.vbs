Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "D:\Nexa ai\My-Nexa"
WshShell.Run "C:\Users\almat\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe main.py", 0, False