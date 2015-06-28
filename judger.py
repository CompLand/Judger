#! /bin/python
__author__ = 'Amir Khazaie 733amir@gmail.com'

import sys, os
from filemanager import FileManager
from cmdarghan import CmdArgHan
from defaults import *
from compiler import Compiler

class Judger:
    def __init__(self):
        cmdArgHan = CmdArgHan(sys.argv)
        fileManager = FileManager(cmdArgHan.getCmdArg())
        compiler = Compiler(fileManager.newPaths())
if __name__ == '__main__':
    Judger()
