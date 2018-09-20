from __future__ import unicode_literals

import os
import subprocess
import time 
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
    style = style_from_dict({
                Token.Toolbar:  '#ffffff bg:#333333',
                
                Token.Name:     '#ff0000',
                Token.Status:   '#ff00ff',
                Token.White:    '#ffffff',
                Token.Pound:    '#ffa500',
                })
   
    def get_bottom_toolbar_tokens(self, cli):
        if self.global_status:
            global_status = self.global_status()
            return [(Token.Toolbar, global_status)]
        else:
            return [(Token.Toolbar, 'welcome to welprompt')]
        
    def __init__(self, name=''):
        self.startinfo = '''START'''
        self.exitinfo = '''End'''
        self.history_file = ''
        self.commands = {'help':self.help}
        self.globals = []
        self.prompt_status = None
        self.global_status = None
        self.name = name
                        
    def get_prompt_tokens(self, cli):
        if self.prompt_status:
            prompt_status = self.prompt_status()
            return [
                (Token.Name,   self.name),
                (Token.White,  ' ['),
                (Token.Status, prompt_status),
                (Token.White,  '] '),
                (Token.Pound,  '> '),
            ]
        else:
            return [
                (Token.Name,   self.name),
                (Token.Pound,  ' > '),
            ]
        
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
                    get_prompt_tokens=self.get_prompt_tokens,
                    completer=completer,
                    history=history,
                    auto_suggest=AutoSuggestFromHistory(),
                    get_bottom_toolbar_tokens=self.get_bottom_toolbar_tokens,
                    patch_stdout=True,
                    mouse_support=True,
                    true_color=True,
                    style=self.style)
                    
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
            if command in self.commands.keys():
                return self.commands[command](*args)
            else:
                return 'no such command'
            
    def _execve(self, cmd):
        return os.popen(cmd).read()
        
    def help(self, *args):
        '''help msg'''
        msg = ''
        if args == (): args = self.commands.keys()
        for command in args:
            if command in self.commands.keys():
                msg += '{}:{}\n'.format(command, 
                    self.commands[command].__doc__)
            else:
                msg += '{}:{}\n'.format(command, 
                    'unkown command')
            
        return msg

if __name__ == '__main__':
    c = CLUI('myapp')
    c.startinfo = '''Tiny Torjan Server CLI'''
    c.exitinfo = '''Closing all stuff'''
    
    def printf(fmt, *args):
        '''this is printf'''
        print(fmt % args)
        
    def prompt_status():
        return os.getcwd()
    def global_status():
        return time.ctime()
        
    c.prompt_status = prompt_status
    c.global_status = global_status
    c.commands['printf'] = printf
    c.run()