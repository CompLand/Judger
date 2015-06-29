#! /bin/python
__author__ = 'Amir Khazaie 733amir@gmail.com'

import sys, os
from filemanager import FileManager
from cmdarghan import CmdArgHan
import defaults as df
from compiler import Compiler

class Judger:
    def __init__(self):
        cmdArgHan = CmdArgHan(sys.argv)
        fileManager = FileManager(cmdArgHan.getCmdArg())
        data = fileManager.newPaths()
        compiler = Compiler(data[df.sourceLanguage], data[df.compiler], data[df.source],
                            os.path.join(fileManager.tempDirPath(), df.tempExeFile))
        print(compiler.status())
if __name__ == '__main__':
    Judger()
