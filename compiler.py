#! /bin/python
__author__ = 'Amir Khazaie 733amir@gmail.com'

import subprocess as sp
import os

# _comcom_ is a dictionary with keys that are Language and values that are Compiler Command as a list with one string.
comcom = {
    'c': 'gcc',
    'c++': 'g++',
    'java': 'javac'
}
# _defarg_ is a dictionary with keys that are Compiler Command and values that are Default Arguments as list.
defarg = {
    'gcc': [],
    'g++': [],
    'javac': []
}
# _outarg_ is compiler argument for put the output file in specific folder
outarg = {
    'gcc': '-o',
    'g++': '-o',
    'javac': '-d'
}

class Compiler:
    def __init__(self, language, compilerarguments, pathtosource, pathforexe):
        self.setcommand(language, compilerarguments, pathtosource, pathforexe)
        self.compile()

    def setcommand(self, lan, comarg, srcpath, exepath):
        self.command = [comcom[lan]] + (comarg and comarg or defarg[comcom[lan]])
        self.command += [outarg[comcom[lan]], exepath]
        self.command += [srcpath]

    def compile(self):
        compro = sp.Popen(self.command, stdout=sp.PIPE, stderr=sp.PIPE)
        self.error = compro.communicate()[1].decode()

    def status(self):
        if self.error:
            return self.error
        return None

if __name__ == '__main__':
    print('''Running test for module. In this test module make a 'TEST.c' file alongside module file,then
compile it. If you see no errors and see the 'Hello World!' on output, logic of module is fine.
''')
    testfile = open('TEST.c', 'w')
    testfile.write('''#include <stdio.h>\nint main(int argc, char const *argv[])\n{\n
    printf("Hello World!\\n");\n    return 0;\n}''')
    testfile.close()
    print('Compiling ...')
    compiler = Compiler('c', [], 'TEST.c', 'TEST')
    if compiler.status():
        print('Compiler error:')
        print(compiler.status())
    else:
        print('Compiled successfully.')
        print('Running executable file ...')
        exetest = sp.Popen('./TEST', stdout=sp.PIPE, stderr=sp.PIPE)
        output, error = exetest.communicate()
        print('TEST output:')
        print(output.decode())
        if error:
            print('TEST error:')
            print(error)
    os.remove('TEST.c')
    os.remove('TEST')
