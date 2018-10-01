# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import subprocess
import time 
import six
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

class MatchCompleter(Completer):
    def __init__(self, get_candidate, 
            ignore_case=False, meta_dict=None, match_middle=False):
        self.get_candidate = get_candidate
        self.ignore_case = ignore_case
        self.meta_dict = meta_dict or {}
        self.match_middle = match_middle

    def get_completions(self, document, complete_event):
        # Get word/text before cursor.
        def word_matches(word):
            if self.ignore_case:
                word = word.lower()
            if self.match_middle:
                return word_before_cursor in word
            else:
                return word.startswith(word_before_cursor)
        text_before_cursor = document.text_before_cursor
        words = text_before_cursor.split()
        if text_before_cursor=='':
            words.append('')
        elif text_before_cursor[-1]==' ':
            words.append('')
    
        words_num = len(words)
        words_before = words[:-1]
        candidates = self.get_candidate(words_before)
        word_before_cursor = words[-1]

        if self.ignore_case:
            word_before_cursor = word_before_cursor.lower()

        for a in candidates:
            if word_matches(a):
                display_meta = self.meta_dict.get(a, '')
                yield Completion(a, -len(word_before_cursor), display_meta=display_meta)
 
            
        
class CLUI(object):
    #https://www.computerhope.com/htmcolor.htm
    style = style_from_dict({
                Token.Toolbar:  '#000000 bg:#C0C0C0',
                
                Token.Name:     '#ff0000',
                Token.Status:   '#00FFFF',
                Token.White:    '#ffffff',
                Token.Pound:    '#00ff00',
                })
   
    def get_bottom_toolbar_tokens(self, cli):
        if self.global_status:
            global_status = self.global_status()
            return [(Token.Toolbar, global_status)]
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
        self.prompt_status = None
        self.global_status = None
        self.name = name
        
    @property
    def words_map(self):
        words_map = {}
        for cmd in self.commands:
            candidates = []
            doc = self.commands[cmd].__doc__.splitlines()
            for line in doc:
                if line.startswith('candidates:'):
                    candidates = line[11:].split()
            words_map[cmd] = candidates
        return words_map
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
    def get_candidate(self, words):
        words_map = self.words_map
        if words==[]:
            return words_map.keys()
        elif len(words)==1:
            if words[0] in words_map:
                return words_map[words[0]]
            else:
                return []
        else:
            return []
    def run(self):
        print(self.startinfo)
        if self.history_file == '':
            history = InMemoryHistory()
        else:
            history = FileHistory(os.path.expanduser(self.history_file))
        completer = MatchCompleter(self.get_candidate)
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
                print('KeyboardInterrupt')
                continue
            except EOFError:
                break
                
        print(self.exitinfo)
    def _handler(self, text):
        if text == '':
            return
        elif text[0] == '!':
            return self._execve(text[1:])
        
        elif text[0] == '%':
            try:
                six.exec_(text[1:], locals(), globals())
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
        
        msg = '?: alias of help\n!: execve shell command\n%: exec python script\nctrl+d: exit\n'
        if args == (): args = self.commands.keys()
        for command in args:
            if command in self.commands.keys():
                nindent = '\n  '+' '*len(command)
                doc = self.commands[command].__doc__
                doc = doc.splitlines()
                doc = nindent.join(doc)
                msg += '{}: {}\n'.format(command, 
                    doc)
            else:
                msg += '{}: {}\n'.format(command, 
                    'unkown command')
            
        return msg

if __name__ == '__main__':
    c = CLUI('myapp')

    def printf(fmt, *args):
        '''no arg'''
        print(fmt % args)

    def mycommand(cmd):
        '''candidates:cand1 cand2 fteawta
tsetes'''
        print(cmd)
        
    def prompt_status():
        return os.getcwd()
    def global_status():
        return time.ctime()
        
    c.prompt_status = prompt_status
    c.global_status = global_status
    c.commands['printf'] = printf
    c.commands['mycommand'] = mycommand
    c.run()