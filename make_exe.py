#!/usr/bin/python

import os
import subprocess

pyinpfad = "C:\Python25\pyinstaller_1.3"
exemakepfad = "D:/dxf2gcode_exe_tkinter"
pyt = "C:/Python25/pythonw.exe"
filepfad= "D:/dxf2gcode/tags/2009-06-04_b02_tkinter"
icon= "D:/dxf2gcode/tags/2009-06-04_b02_tkinter/DXF2GCODE-001.ico"
file = "dxf2gcode_b02"


options=("--onefile --noconsole --upx --tk --icon=%s" %icon)
print options

#Verzwichniss wechseln
exemakepfad = unicode( exemakepfad, "utf-8" )
os.chdir(exemakepfad.encode( "utf-8" ))


cmd=("%s %s\Makespec.py %s %s/%s.py" %(pyt,pyinpfad,options,filepfad,file))
print cmd
retcode=subprocess.call(cmd)

cmd=("%s %s\Build.py %s\%s.spec" %(pyt,pyinpfad,exemakepfad,file))
print cmd
retcode=subprocess.call(cmd)

print "\n!!!!!!!Bitmaps und Languagues Ordner nicht vergessen!!!!!!"
print "\nFertig"