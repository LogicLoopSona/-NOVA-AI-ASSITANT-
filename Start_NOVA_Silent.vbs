' Launches NOVA using pythonw.exe — completely silent, NO console/terminal window.
' Only the NOVA circle GUI window will appear.
Set fso = CreateObject("Scripting.FileSystemObject")
strPath = fso.GetParentFolderName(WScript.ScriptFullName)
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = strPath
WshShell.Run "pythonw.exe main.py", 0, False
