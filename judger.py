#! /usr/bin/env python3
__author__ = 'Amir Khazaie, Isfahan University of Technology Student, Email: 733amir@gmail.com'

'''
Auto-Judging script written in python.
This script needs no root permission.
Currently support C, C++, Java with just one source code.
There is 2 way to use this script:
1- Commandline
2- Import it in your script, call Judger function and pass the arguments
This script is written by CompLand/Amir Khazaie
Copyright 2015
'''

from os import remove
from os.path import isfile, join, split
from tempfile import TemporaryDirectory
from shutil import copy
from subprocess import Popen, PIPE, TimeoutExpired
from time import time
from json import dump
from threading import Thread
from psutil import Process, NoSuchProcess
from argparse import ArgumentParser

sup_lan = supported_languages = ["c", "c++", "cpp", "java"]
def_com_arg = default_compiler_arguments = {
    'c': '',
    'c++': '',
    'cpp': '',
    'java': ''
}

def writable(path):
    try:
        open(path, 'w')
    except RuntimeError:
        return False
    remove(path)
    return True

def file_name_check(lan, path):
    file_name = split(path)[1]
    if '.' not in file_name:
        return False
    file_name_main, file_name_extension = file_name.split('.')
    if lan == 'java' and file_name_extension == 'java':
        return True
    elif lan == 'c' and file_name_extension == 'c':
        return True
    elif lan in ['c++', 'cpp'] and file_name_extension == 'cpp':
        return True
    return False

def input_output_list_builder(input_directory_path, output_directory_path):
    i = 1
    input_list = []
    output_list = []
    while True:
        input_file = join(input_directory_path, '%d.in' % i)
        output_file = join(output_directory_path, '%d.out' % i)
        if isfile(input_file) and isfile(output_file):
            input_list.append(input_file)
            output_list.append(output_file)
            i += 1
        elif i == 1:
            raise InputOutputFileError('No Input-Output paired file')
        else:
            break
    return (input_list, output_list)

def command_line_argument_handler():
    parser = ArgumentParser(
            description='This python script is auto-judging codes.',
            add_help=True
        )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='Version Alpha'
    )
    parser.add_argument(
        '-l', '--language',
        dest='language', default='c',
        help='language of source code you want to be judged (lowercase)',
        choices=(sup_lan)
    )
    parser.add_argument(
        '-t', '--time-limit',
        type=int, dest='time_limit', default='5',
        help='time limit for the code (integer of seconds)'
    )
    parser.add_argument(
        '-m', '--memory-limit',
        type=int, dest='memory_limit', default='16',
        help='memory limit for the code (integer of MB)'
    )
    parser.add_argument(
        '-i', '--input-directory-path',
        dest='input_path', default='.',
        help='relative or absolute path to input directory'
    )
    parser.add_argument(
        '-o', '--output-directory-path',
        dest='output_path', default='.',
        help='relative or absolute path to output directory'
    )
    parser.add_argument(
        '-r', '--result-directory-path',
        dest='result_path', default='.',
        help='relative or absolute path to result directory'
    )
    parser.add_argument(
        '-c', '--compiler-args',
        dest='compiler_args', default=None,
        help='compiler options (put them in double quotes)'
    )
    parser.add_argument(
        dest='source_path',
        help='relative or absolute path to source file')
    return parser.parse_args()

def Judger(language='c', time_limit='5', memory_limit='16', input_directory_path='.', output_directory_path='.',
         result_directory_path='.', source_file_path='source.c', compiler_arguments=None):
    in_list, out_list = input_output_list_builder(input_directory_path, output_directory_path)
    Judge(language, time_limit, memory_limit, in_list, out_list, source_file_path, result_directory_path,
          compiler_arguments)


class InputOutputFileError(RuntimeError):
    def __init__(self, arg):
        self.arg = arg


class Judge:
    def __init__(self, language, time_limit, memory_limit, input_files_path_list, output_files_path_list,
                 source_file_path, result_directory_path, compiler_arguments=None):
        self.__lan = language
        self.__tim_lim = time_limit
        self.__mem_lim = memory_limit * 1024 * 1024
        self.__inp_lis = input_files_path_list
        self.__out_lis = output_files_path_list
        self.__src = source_file_path
        self.__res = result_directory_path
        if compiler_arguments:
            self.__com_arg = compiler_arguments
        else:
            self.__com_arg = def_com_arg[language]
        self.__copy_files()
        if self.__compile():
            self.__run()

    def __copy_files(self):
        self.__tmp_dir = TemporaryDirectory()
        new_list = []
        i = 1
        for address in self.__inp_lis:
            new_address = join(self.__tmp_dir.name, "%d.in" % i)
            copy(address, new_address)
            new_list.append(new_address)
            i += 1
        self.__inp_lis = new_list.copy()
        new_list.clear()
        i = 1
        for address in self.__out_lis:
            new_address = join(self.__tmp_dir.name, "%d.out" % i)
            copy(address, new_address)
            new_list.append(new_address)
            i += 1
        self.__out_lis = new_list.copy()
        copy(self.__src, self.__tmp_dir.name)
        file_name = split(self.__src)[1]
        self.__src = join(self.__tmp_dir.name, file_name)
        self.__exe = join(self.__tmp_dir.name, file_name.split('.')[0])

    def __compile(self):
        command = []
        if self.__lan == 'c':
            command.append('gcc')
        elif self.__lan in ['c++', 'cpp']:
            command.append('g++')
        elif self.__lan == 'java':
            command.append('javac')
        if self.__com_arg:
            command.extend(self.__com_arg.split())
        if self.__lan in ['c', 'c++', 'cpp']:
            command.append('-o')
            command.append(self.__exe)
        elif self.__lan == 'java':
            command.append('-d')
            command.append(self.__tmp_dir.name)
        command.append(self.__src)
        output, error = Popen(command, stdout=PIPE, stderr=PIPE).communicate()
        if error:
            self.__write_status('res', 'CE', error.decode(), 0, 0)
            return False
        return True

    def __run(self):
        if self.__lan == 'java':
            self.__exe = ['java', self.__exe]
        l = [(self.__inp_lis[i], self.__out_lis[i]) for i in range(len(self.__inp_lis))]
        results = []
        i = 0
        for input_path, output_path in l:
            i += 1
            p = Popen(self.__exe, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            data = [p.pid, p.kill]
            t = Thread(target=self.__memory_watcher, args=(data,))
            t.start()
            try:
                start_time = time()
                o, e = p.communicate(bytes(open(input_path).read(), 'ascii'), self.__tim_lim)
                end_time = time()
            except TimeoutExpired:
                p.kill()
                self.__write_status('%d.res' % i, 'TLE', '', self.__tim_lim, 0)
                results.append('TLE')
            else:
                t.join()
                if data[2] > self.__mem_lim:
                    self.__write_status('%d.res' % i, 'MLE', '', end_time - start_time, data[2])
                    results.append('MLE')
                elif p.returncode != 0:
                    self.__write_status('%d.res' % i, 'RE', e.decode(), end_time - start_time, data[2])
                    results.append('RE')
                elif o.decode() != open(output_path).read():
                    self.__write_status('%d.res' % i, 'WA', '', end_time - start_time, data[2])
                    results.append('WA')
                else:
                    self.__write_status('%d.res' % i, 'AC', '', end_time - start_time, data[2])
                    results.append('AC')
        tle_count = mle_count = re_count = wa_count = ac_count = 0
        for result in results:
            if result == 'AC':
                ac_count += 1
            elif result == 'WA':
                wa_count += 1
            elif result == 'RE':
                re_count += 1
            elif result == 'MLE':
                mle_count += 1
            elif result == 'TLE':
                tle_count += 1
        self.__write_status('res', None, None, None, None, {
            'status': 'CS',
            'AC': ac_count,
            'WA': wa_count,
            'RE': re_count,
            'MLE': mle_count,
            'TLE': tle_count
        })

    def __memory_watcher(self, data):
        max_memory = 0
        try:
            p = Process(data[0])
            memory = 1
            while 0 < memory and max_memory <= self.__mem_lim:
                memory = p.memory_info()[0] - p.memory_info_ex().shared
                if max_memory < memory:
                    max_memory = memory
            data[1]()
        except NoSuchProcess:
            pass
        finally:
            data.append(max_memory)

    def __write_status(self, name, status, error, time, memory, data=None):
        if data == None:
            data = {
                'status': status,
                'error': error,
                'time': time,
                'memory': memory
            }
        result_file = open(join(self.__res, name), 'w')
        dump(data, result_file)
        result_file.close()


if __name__ == '__main__':
    n = command_line_argument_handler()
    in_list, out_list = input_output_list_builder(n.input_path, n.output_path)
    Judge(n.language, n.time_limit, n.memory_limit, in_list, out_list, n.source_path, n.result_path, n.compiler_args)
