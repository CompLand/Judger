from json import dump
from time import sleep, time
from shutil import copy
from psutil import Process, NoSuchProcess
from os.path import isfile, join, split
from argparse import ArgumentParser
from tempfile import TemporaryDirectory
from threading import Thread
from subprocess import Popen, PIPE, TimeoutExpired

supported_languages = ['c', 'c++', 'java']
filtering_categories = ['acm']
compiler_command = {
    'c': 'gcc',
    'c++': 'g++',
    'cpp': 'g++',
    'java': 'javac',
}

def readable(path):
    try:
        open(path)
    except RuntimeError:
        return False
    return True

def writable(path):
    try:
        open(path, 'w')
    except RuntimeError:
        return False
    return True


class InputArgumentsError(RuntimeError):
    def __init__(self, arg):
        self.arg = arg


class CompilerError(RuntimeError):
    def __init__(self, arg):
        self.arg = arg


class Judge:
    def judge(self, language, time_limit, memory_limit, input_path,
                 output_path, source_path, result_path = None, diff_args = "",
                 compiler_args = "", forbidden_category = "acm"):
        self.__check_args(language, time_limit, memory_limit, input_path,
                 output_path, result_path, diff_args, compiler_args,
                 forbidden_category, source_path)
        self.__src_lan = language
        self.__com_com = compiler_command[language]
        self.__tim_lim = time_limit
        self.__mem_lim = memory_limit * 1024 * 1024
        self.__inp_pat = input_path
        self.__out_pat = output_path
        self.__res_pat = result_path
        self.__dif_arg = diff_args
        self.__com_arg = compiler_args
        self.__for_cat = forbidden_category
        self.__src_pat = source_path
        self.__judgement()

    def run_module(self):
        parser = ArgumentParser(
            description='This python script is auto-judging codes.',
            add_help=True
        )
        parser.add_argument(
            '-v', '--version',
            action='version',
            version='Version Pre-alpha'
        )
        parser.add_argument(
            '-l', '--language',
            dest='language',
            help='language of source code you want to be judged (lowercase)',
            choices=(supported_languages)
        )
        parser.add_argument(
            '-t', '--time-limit',
            type=int, dest='time_limit',
            help='time limit for the code (integer of seconds)'
        )
        parser.add_argument(
            '-m', '--memory-limit',
            type=int, dest='memory_limit',
            help='memory limit for the code (integer of MB)'
        )
        parser.add_argument(
            '-i', '--input-path',
            dest='input_path',
            help='relative or absolute path to input file'
        )
        parser.add_argument(
            '-o', '--output-path',
            dest='output_path',
            help='relative or absolute path to output file'
        )
        parser.add_argument(
            '-r', '--result-path',
            dest='result_path',
            help='relative or absolute path including the name of result file'
        )
        parser.add_argument(
            '-d', '--diff-args',
            dest='diff_args',
            help='diff options to compare (put them in double quotes)'
        )
        parser.add_argument(
            '-c', '--compiler-args',
            dest='compiler_args',
            help='compiler options (put them in double quotes)'
        )
        parser.add_argument(
            '-f', '--forbidden-syntax',
            dest='forbidden_category',
            help='select a category for checking forbidden syntax',
            choices=(filtering_categories)
        )
        parser.add_argument(
            dest='source_path',
            help='relative or absolute path to source file')
        n = parser.parse_args()
        self.judge(n.language, n.time_limit, n.memory_limit, n.input_path,
                   n.output_path, n.source_path, n.result_path, n.diff_args,
                   n.compiler_args, n.forbidden_category)

    def __check_args(self, lan, tim, mem, inp, out, res, dif, com, frb, src):
        error = ''
        if lan not in supported_languages:
            error = 'Language not supported.'
        elif not isinstance(tim, int):
            error = 'Time_limit is not integer.'
        elif not isinstance(mem, int):
            error = 'Memory_limit is not integer.'
        elif not isfile(inp):
            error = 'Input_path not pointing to a file.'
        elif not readable(inp):
            error = 'Input file is not readable.'
        elif not isfile(out):
            error = 'Output_path not pointing to a file.'
        elif not readable(out):
            error = 'Output file is not readable.'
        elif res:
            if not writable(res):
                error = 'Can\'t write result file.'
        elif not frb in filtering_categories:
            error = 'No category named \'%s\'.' % frb
        elif not isfile(src):
            error = 'Source_path not pointing to a file.'
        elif not readable(src):
            error = 'Source file is not readable.'
        if error:
            raise InputArgumentsError(error)

    def __judgement(self):
        global max_memory, max_memory
        self.__copy_files()
        try:
            self.__compile()
        except CompilerError as e:
            self.__set_status('CE', e.arg, 0, 0)
        else:
            data = {}
            run_thread = Thread(target=self.__run, args=(data,))
            run_thread.start()
            while not data.get('pid'):
                pass
            max_memory = 0
            process_ended = False
            try:
                p = Process(data['pid'])
                max_memory = p.memory_info()[0] #- p.memory_info_ex().shared
                memory = p.memory_info()[0] #- p.memory_info_ex().shared
                while max_memory <= self.__mem_lim and memory != 0:
                    memory = p.memory_info()[0] #- p.memory_info_ex().shared
                    if max_memory < memory:
                        max_memory = memory
            except NoSuchProcess:
                process_ended = True
            else:
                data['kill']()
            while not data.get('time'):
                pass
            if max_memory > self.__mem_lim:
                self.__set_status('MLE', '', 0, max_memory )
            elif data['time'] == self.__tim_lim:
                self.__set_status('TLE', '', self.__tim_lim, max_memory)
            elif data['return']:
                self.__set_status('RE', '', data['time'], max_memory)
            elif data['output'] == open(self.__out_pat).read():
                self.__set_status('AC', '', data['time'], max_memory)
            else:
                self.__set_status('WA', '', data['time'], max_memory)
        if self.__res_pat:
            self.__write_status()

    def __copy_files(self):
        self.__tmp_pat = TemporaryDirectory()
        copy(self.__inp_pat, self.__tmp_pat.name)
        self.__inp_pat = join(self.__tmp_pat.name, split(self.__inp_pat)[1])
        copy(self.__out_pat, self.__tmp_pat.name)
        self.__out_pat = join(self.__tmp_pat.name, split(self.__out_pat)[1])
        copy(self.__src_pat, self.__tmp_pat.name)
        self.__src_pat = join(self.__tmp_pat.name, split(self.__src_pat)[1])
        if self.__src_lan in ['c', 'c++', 'cpp']:
            self.__exe_pat = join(self.__tmp_pat.name, 'exe')
        elif self.__src_lan == 'java':
            self.__exe_pat = join(self.__tmp_pat.name,
                                split(self.__src_pat)[1][:-5] + '.class')

    def __compile(self):
        command = [self.__com_com]
        if self.__com_arg:
            command += [self.__com_arg]
        if self.__src_lan == 'java':
            command += ['-d', self.__tmp_pat.name]
        elif self.__src_lan in ['c', 'c++']:
            command += ['-o', self.__exe_pat]
        command += [self.__src_pat]
        error = Popen(command, stdout=PIPE, stderr=PIPE).communicate()[1]
        if error:
            raise CompilerError(error.decode())

    def __run(self, data):
        input_string = open(self.__inp_pat, 'r').read()
        command = None
        if self.__src_lan in ['c', 'c++']:
            command = self.__exe_pat
        elif self.__src_lan == 'java':
            class_name = split(self.__src_pat)[1][:-5]
            command = ['java', class_name]
        program = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        data['pid'] = program.pid
        data['kill'] = program.kill
        start_time = time()
        try:
            output, error = program.communicate(bytes(input_string, 'ascii'),
                                                self.__tim_lim)
            data['return'] = program.returncode
            data['time'] = time() - start_time
        except TimeoutExpired:
            data['time'] = self.__tim_lim
            program.kill()
        else:
            data['output'] = output.decode()
            data['error'] = error.decode()

    def __set_status(self, status, error, time, memory):
        self.__sts = status
        self.__err = error
        self.__tim = time
        self.__mem = memory

    def __write_status(self):
        data = {
            'status': self.__sts,
            'error': self.__err,
            'time': self.__tim,
            'memory': self.__mem
        }
        res_fle = open(self.__res_pat, 'w')
        dump(data, res_fle)
        res_fle.close()

    def status(self):
        return (self.__sts, self.__err, self.__tim, self.__mem)

if __name__ == '__main__':
    Judge().run_module()
