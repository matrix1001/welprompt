# welprompt
a light CLUI tools for quickly constructing your python tools
# install
```python
python setup.py install
```
# usage
```python
def this_is_your_function(cmd):
    '''candidates:ls pwd hello'''
    print(cmd)
from welprompt import CLUI
clui = CLUI('myapp')
clui.commands['this_is_your_function']=this_is_your_function
clui.run()
```
u will get this.
```
██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗███████╗
██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██╔════╝
██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║█████╗
██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██╔══╝
╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗
 ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝


myapp > this_is_your_function hello
hello
myapp >

```