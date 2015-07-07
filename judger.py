#! /usr/bin/python3
__author__ = 'Amir Khazaie 733amir@gmail.com'

import os
import json
import argparse
import tempfile
import subprocess
from shutil import copy


# Some default arguments for project.
supported_languages = ['c', 'c++', 'java']
filtering_categories = ['acm']
compiler_command = {
    'c': 'gcc',
    'c++': 'g++',
    'java': 'javac'
}
default_arguments = {
    'gcc': '',
    'g++': '',
    'javac': ''
}
necessary_argument_for_output = {
    'gcc': '-o',
    'g++': '-o',
    'javac': '-d'
}
language_file_extension = {
    'c': '.c',
    'c++': '.cpp',
    'java': '.java'
}


# Exceptions
class InputArgumentsError(RuntimeError):
    def __init__(self, arg):
        self.arg = arg


class CompilerError(RuntimeError):
    def __init__(self, arg):
        self.arg = arg

# Judger Object
class Judger:
    """
 This script is written for linux systems in python3. The Judger will judge
specific code with input and compare the output. Result of judgement is in
result file.
"""

    def set(self, language, time_limit, memory_limit, input_path, output_path, result_path, diff_args, compiler_args,
            forbidden_category, source_path, test):
        """
 For using this judge you should passed information that is necessary with
this function.

    Exception(s):
        None
    Function parameter(s):
        language: Language of source code.
        time_limit: Time limit in seconds that program must run, get input,
            print output and ends.
        memory_limit: Memory limit in Mega Bytes that program must run, get
            input, print output and ends.
        input_path: Relative or absolute path to input file for program.
        output_path: Relative or absolute path to output file to compare with
            the program output.
        result_path: Relative or absolute path containing name of file to
            write the result in it.
        diff_args: Linux `diff` command to compare th output of the program
            with the output file pass by user (`output_path`). Define it with
            double-quotes.
        compiler_args: Compiler arguments for the compiler to compile the
            source code.
        forbidden_category: Selected category to define a restriction of
            the source code accessibility.
        source_path: Relative or absolute path to source code file.
        test: A boolean, if True the whole module will be tested otherwise
            module works normal.
    Function return:
        None
"""
        self.language = language
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.input_path = input_path
        self.output_path = output_path
        self.result_path = result_path
        self.diff_args = diff_args
        self.compiler_args = compiler_args
        self.forbidden_category = forbidden_category
        self.source_path = source_path
        self.test = test
        self.check_args()
        self.memory_limit = self.memory_limit * 1024 * 1024
        self.imported_module = True

    def handle_command_line_argument(self):
        """
 Handling arguments passed in the command line and add them to `Judge`
namespace.

    Exception(s):
        None
    Function parameter(s):
        None
    Function return:
        None
"""
        parser = argparse.ArgumentParser(description='This python script is auto-judging codes.', add_help=True)
        parser.add_argument('-v', '--version', action='version', version='Version Pre-alpha')
        parser.add_argument('-l', '--language', dest='language',
                            help='language of source you want to be judged (lowercase)', choices=(supported_languages))
        parser.add_argument('-t', '--time-limit', type=int, dest='time_limit',
                            help='time limit for the code (integer of seconds)')
        parser.add_argument('-m', '--memory-limit', type=int, dest='memory_limit',
                            help='memory limit for the code (integer of MB)')
        parser.add_argument('-i', '--input-path', dest='input_path',
                            help='relative or absolute path to input file')
        parser.add_argument('-o', '--output-path', dest='output_path',
                            help='relative or absolute path to output file')
        parser.add_argument('-r', '--result-path',  dest='result_path',
                            help='relative or absolute path containing the name of result file')
        parser.add_argument('-d', '--diff-args', dest='diff_args',
                            help='diff options to compare (put them in double quotes)')
        parser.add_argument('-c', '--compiler-args', dest='compiler_args',
                            help='compiler options (put them in double quotes)')
        parser.add_argument('-f', '--forbidden-syntax', dest='forbidden_category',
                            help='select a category for checking forbidden syntax.', choices=(filtering_categories))
        parser.add_argument(dest='source_path',
                            help='relative or absolute path to source file')
        parser.add_argument('-test', action='store_true', dest='test',
                            help='run complete test on whole project', default=False)
        parser.parse_args(namespace=self)
        self.check_args()
        self.memory_limit = self.memory_limit * 1024 * 1024
        self.imported_module = False

    def check_args(self):
        """
 Checking correctness of the passed arguments to avoid exceptions and problems
caused by the value of this arguments.

    Exception(s):
        `InputArgumentsError` with string argument that explains the error
    Function parameter(s):
        None
    Function return:
        None
"""
        error = ''
        if self.language not in supported_languages:
            error = 'Language not supported.'
        elif type(self.time_limit) is not int:
            error = 'Time limit is not integer.'
        elif type(self.memory_limit) is not int:
            error = 'Memory limit is not integer.'
        elif not os.path.isfile(self.input_path):
            error = 'Input path not pointing to a file.'
        elif not os.access(self.input_path, os.R_OK):
            error = 'Input file is not readable.'
        elif not os.path.isfile(self.output_path):
            error = 'Output path not pointing to a file.'
        elif not os.access(self.output_path, os.R_OK):
            error = 'Output file is not readable.'
        elif not self.writable(self.result_path):
            error = 'Can\'t write result file.'
        elif not self.forbidden_category in filtering_categories:
            error = 'No category named \'%s\'.' % self.forbidden_category
        elif not os.path.isfile(self.source_path):
            error = 'Source path not pointing to a file.'
        elif not os.access(self.source_path, os.R_OK):
            error = 'Source file is not readable.'
        if error:
            raise InputArgumentsError(error)

    def writable(self, path):
        """
 Checking writability of the path.

    Exception(s):
        None
    Function parameter(s):
        path: relative or absolute path to a file
    Function return:
        bool: True if can make file and write to it otherwise False.
"""
        try:
            f = open(path, 'w')
        except IOError:
            return False
        f.close()
        return True

    def compiler(self):
        """
 By using the information at the first of this script, the ones that defined
to carry defaults options and arguments, it will compile the source code to a
specific binary data to run.

    Exception(s):
        `CompilerError` with string argument that explain the error.
    Function parameter(s):
        None
    Function return:
        None
"""
        command = [compiler_command[self.language]] +\
                  [self.compiler_args and self.compiler_args or default_arguments[compiler_command[self.language]]] +\
                  [necessary_argument_for_output[compiler_command[self.language]], self.executable_file_path] +\
                  [self.source_path]
        error = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[1].decode()
        if error:
            raise CompilerError(error)

    def runner(self):
        pass

    def judge(self):
        """
 This is the main function that you should call. But before calling this you
have to set information that judger needs with `handle_command_line_argument`
function or `set` function.

    Exception(s):
        None
    Function parameter(s):
        None
    Function return:
        None
"""
        self.copy_files()
        try:
            self.compiler()
        except CompilerError as e:
            self.set_result('CE', e.arg, 0, 0)
            if not self.imported_module:
                self.write_result_file()
        else:
            # TODO write a runner function in here
            pass

    def copy_files(self):
        """
 To judge the code with specific input and output, we copy all necessary files
in a temporary directory in the system, because maybe at the judging time the
files could be deleted or moved or ... that there is no longer access to the
content of those files.

    Exception(s):
        None
    Function parameter(s):
        None
    Function return:
        None
"""
        self.temporary_directory_path = tempfile.TemporaryDirectory()
        copy(self.input_path, os.path.join(self.temporary_directory_path.name, 'input'))
        self.input_path = os.path.join(self.temporary_directory_path.name, 'input')
        copy(self.output_path, os.path.join(self.temporary_directory_path.name, 'output'))
        self.output_path = os.path.join(self.temporary_directory_path.name, 'output')
        copy(self.source_path, os.path.join(self.temporary_directory_path.name, 'source' +\
                                            language_file_extension[self.language]))
        self.source_path = os.path.join(self.temporary_directory_path.name, 'source' +\
                                        language_file_extension[self.language])
        self.executable_file_path = os.path.join(self.temporary_directory_path.name, 'exe')

    def set_result(self, status, error, time, memory):
        """
 Set result to class attributes.

    Exception(s):
        None
    Function parameter(s):
        status: Status to write in the file.
        error: Error to write in the file.
        time: Used time to write in the file.
        memory: Used memory to write in the file.
    Function return:
        None
"""
        self.status = status
        self.error = error
        self.time = time
        self.memory = memory

    def write_result_file(self):
        """
 Judge provide information about judgement and write them to file with path
of `result_path` with format of `JSON`. The json file is like this:
{
    "status": Status of the judgement that can be "AC" as Accepted, "WA" as
              Wrong Answer, "RE" as Runtime Error, "TLE" as Time Limit
              Exceeded, "MLE" as Memory Limit Exceeded, "OLE" as Output Limit
              Exceeded and "IE" as Internal Error.
    ,
    "error": Explanation of the error that happened.
    ,
    "time": Time spend to run the code.
    ,
    "memory": Memory used to run the code.
}

    Exception(s):
        None
    Function parameter(s):
        None
    Function return:
        None
"""
        data = {
            'status': self.status,
            'error': self.error,
            'time': self.time,
            'memory': self.memory
        }
        result_file = open(self.result_path, 'w')
        json.dump(data, result_file)
        result_file.close()

    def result(self):
        """
 Returns a tuple of current judgment status.

    Exception(s):
        None
    Function parameter(s):
        None
    Function return:
        (status, error, time, memory)
"""
        return (self.status, self.error, self.time, self.memory)

if __name__ == '__main__':
    j = Judger()
    j.handle_command_line_argument()
    j.judge()
