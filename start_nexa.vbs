Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "D:\lut\Mark-LIV-main"
WshShell.Run "python main.py", 0, False