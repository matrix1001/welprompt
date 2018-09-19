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
                Token.Toolbar: '#ffffff bg:#333333',
                })
   
    def get_bottom_toolbar_tokens(self, cli):
        if self.global_info:
            global_info = self.global_info()
            return [(Token.Toolbar, global_info)]
        else:
            return [(Token.Toolbar, 'welcome to welprompt')]
        
    def __init__(self, name=''):
        self.startinfo = '''
██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗███████╗
██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██╔════╝
██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║█████╗  
██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██╔══╝  
╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗
 ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝
                                                              
'''
        #http://patorjk.com/software/taag/#p=display&f=ANSI%20Shadow&t=bye
        self.exitinfo = '''
██████╗ ██╗   ██╗███████╗
██╔══██╗╚██╗ ██╔╝██╔════╝
██████╔╝ ╚████╔╝ █████╗  
██╔══██╗  ╚██╔╝  ██╔══╝  
██████╔╝   ██║   ███████╗
╚═════╝    ╚═╝   ╚══════╝
                         
'''
        self.history_file = ''
        self.commands = {'help':self.help}
        self.globals = []
        self.prompt_info = None
        self.global_info = None
        self.name = name
                        
    @property
    def prompt(self):
        if self.prompt_info:
            prompt_info = self.prompt_info()
            return '%s [%s] > ' % (self.name, prompt_info)
        else:
            return '%s > ' % self.name
        
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
                    get_bottom_toolbar_tokens=self.get_bottom_toolbar_tokens,
                    patch_stdout=True,
                    mouse_support=True,
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
    #c.startinfo = '''Tiny Torjan Server CLI'''
    #c.exitinfo = '''Closing all stuff'''
    
    def printf(fmt, *args):
        '''this is printf'''
        print(fmt % args)
        
    def prompt_info():
        return os.getcwd()
    def global_info():
        return time.ctime()
        
    c.prompt_info = prompt_info
    c.global_info = global_info
    c.commands['printf'] = printf
    c.run()