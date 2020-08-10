import wx
from wx.py.shell import Shell

ID_CONSOLE = 10013


class ConsoleWindow(wx.MDIChildFrame):
    """ConsoleWindow object"""
    title = 'Python Console'
    state = ID_CONSOLE

    def __init__(self, parent=None):
        """ConsoleWindow(parent=None) -> wx.MDIChildFrame"""
        super(ConsoleWindow, self).__init__(parent, title=self.title, style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.namespace = {
            '__name__': '__main__',
            'print': lambda *args, **kwargs: print(*args, **kwargs, file=self.console),
            'input': self.parent.InputFunc
        }
        self.console = Shell(self)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Show(False)

    def OnClose(self, event):
        """Close the window. But it is not closed."""
        self.parent.viewm.Check(ID_CONSOLE, False)
        self.Show(False)
        self.parent.OnTile(event)
