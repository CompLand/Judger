#! /bin/python
__author__ = 'Amir Khazaie 733amir@gmail.com'

import subprocess

class Compiler:

    def __init__(self, language, userArgs, sourcePath, exePath):
        self.sourcePath = [sourcePath]
        self.exePath = exePath
        self.setDefaults()
        self.setLanguage(language)
        self.setCompilerCommand()
        self.setCompilerArgs(userArgs)
        self.compile()

    def setDefaults(self):
        self.compilerof = {
            'c': 'gcc',
            'c++': 'g++',
            'java': 'javac'
        }
        self.defArgs = {
            'gcc': [],
            'g++': [],
            'javac': []
        }
        self.necArgs = {
            'gcc': ['-o', self.exePath],
            'g++': ['-o', self.exePath],
            'javac': ['-d', self.exePath]
        }

    def setLanguage(self, language):
        self.language = language

    def setCompilerCommand(self):
        self.compilerCommand = [self.compilerof[self.language]]

    def setCompilerArgs(self, userArgs):
        if userArgs:
            self.compilerArgs = userArgs
        else:
            self.compilerArgs = self.defArgs[self.compilerCommand[0]]
        self.compilerArgs += self.necArgs[self.compilerCommand[0]]

    def compile(self):
        compilingProcess = subprocess.Popen(self.compilerCommand + self.compilerArgs + self.sourcePath,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, self.error = compilingProcess.communicate()
        self.error = self.error.decode()

    def status(self):
        if self.error:
            return self.error

# if __name__ == '__main__':
#     Compiler('c', [], pathof['source'], pathof['exefile'])
