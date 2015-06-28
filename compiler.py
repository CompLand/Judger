#! /bin/python
__author__ = 'Amir Khazaie 733amir@gmail.com'

from defaults import *
import subprocess, os

class Compiler:
    def __init__(self, data):
        self.data = data

    def compileIt(self):
        subprocess.call([languageCompilerCommand[self.data[sourceLanguage]],
                        self.data[compiler],
                        comArgMovOutToTempDir(languageCompilerCommand[self.data[sourceLanguage]]),
                        self.data[source]])
