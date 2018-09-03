from __future__ import unicode_literals

import os
import subprocess
from time import sleep

from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.shortcuts import print_tokens

from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.history import FileHistory, InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from pygments.token import Token

class CLUI(object):
    def __init__(self):
        self.startinfo = '''START'''
        self.exitinfo = '''End'''
        self.history_file = ''
        self.commands = []
        self.globals = []
                        
    @property
    def prompt(self):
        return '> '
        
    def run(self):
        print(self.startinfo)
        if self.history_file == '':
            history = InMemoryHistory()
        else:
            history = FileHistory(os.path.expanduser(self.history_file))
        completer = WordCompleter(self.commands)
        while True:
            try:
                text = prompt(
                    self.prompt,
                    completer=completer,
                    history=history,
                    auto_suggest=AutoSuggestFromHistory(),
                    patch_stdout=True,
                    mouse_support=True)
                    
                msg = self._handler(text)
                if msg:print(msg)
                
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
                
        print(self.exitinfo)
    def _handler(self, text):
        if text == '':
            return
        elif text[0] == '!':
            return self._execve(text[1:])
        
        elif text[0] == ':':
            try:
                d = dict(locals(), **globals())
                exec(text[1:], d, d)
            except Exception as e:
                return str(e)
            
        elif text[0] == '?':
            return self.help()
        else:
            command = text.split()[0]
            args = []
            if len(text.split()) > 1:
                args = text.split()[1:]
            if command in self.commands:
                return self.__getattribute__(command)(*args)
            else:
                return 'no such command'
            
    def _execve(self, cmd):
        return os.popen(cmd).read()
        
    def help(self, *args):
        msg = ''
        if args == (): args = self.commands
        for command in args:
            if command in self.commands:
                msg += '{}:{}\n'.format(command, 
                    self.__getattribute__(command).__doc__)
            else:
                msg += '{}:{}\n'.format(command, 
                    'unkown command')
            
        return msg

if __name__ == '__main__':
    c = CLUI()
    c.run()