import threading 
from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel

@dataclass
class BoxedconsoleConfigs:
    box_width:int=300
    out_dir:Optional[str]=None


class BoxedConsoleAPI:
    @abstractmethod
    def printb(self,*args,**kwargs):
        ...

    @abstractmethod
    def print(self,*args,**kwargs):
        ...

    @classmethod
    def _make_box_title(cls,title):
        return f"{title} [{cls._thread_id()}]"
    
    @staticmethod
    def _thread_id():
        curr_thr=threading.current_thread()
        return f"{curr_thr.name}@{curr_thr.native_id}"
    

class MockBoxedConsole(BoxedConsoleAPI):
    def printb(self, *args, **kwargs):
        pass

    def print(self, *args, **kwargs):
        pass

class FileConsole(BoxedConsoleAPI):
    def __init__(self,*,out_file,title) -> None:
        self.title=title
        self.out_file=out_file

    def printb(self, message,title=None,*args, **kwargs):
        title=self._make_box_title(title or self.title)
        with open(self.out_file,'a') as fou:
            if title:
                fou.write(f"----{title}------")
            fou.write(message)
            fou.write("\n")

    def print(self, message):
        with open(self.out_file,'a') as fou:
            fou.write(message)
            fou.write("\n")

class BoxConsole(BoxedConsoleAPI):
    def __init__(self,*,box_width,box_title,box_bg_color="black"):
        self.console=Console()
        self.box_width=box_width
        self.box_title=box_title
        self.box_bg_color=box_bg_color

    def printb(self, message,title=None,background=None):
        title=self._make_box_title(self.box_title)
        background=background or self.box_bg_color
        self.console.print(Panel(
            f"{message}",
            title=title,title_align="left",
            width=self.box_width,
            style=f"on {background}"
        ))
    
    def print(self, messsage):
        self.console.print(messsage,width=self.box_width,style=f"on {self.box_bg_color}")


def get_boxed_console(
        box_title=None,
        box_bg_color="black",
        console_name="llm4inv",
        debug_mode=False
    )->BoxedConsoleAPI:
        if debug_mode:
            if BoxedconsoleConfigs.out_dir:
                return FileConsole(
                    out_file=str(
                        (Path(BoxedconsoleConfigs.out_dir) / (console_name+'.log')).resolve()
                    ),
                    title=box_title
                )
            else:
                return BoxConsole(
                    box_width=BoxedconsoleConfigs.box_width,
                    box_title=box_title,
                    box_bg_color=box_bg_color
                )
        else:
            return MockBoxedConsole()
