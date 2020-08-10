import wx

ID_OUTPUT = 10024


class OutputWindow(wx.MDIChildFrame):
    """A frame that print something"""
    title = 'Output'
    state = ID_OUTPUT

    def __init__(self, parent=None):
        """OutputWindow(parent=None) -> wx.Frame

        The place where it print something.
        """
        super(OutputWindow, self).__init__(parent, title=self.title, style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.output = wx.TextCtrl(
            self,
            style=(
                    wx.TE_MULTILINE
                    | wx.TE_READONLY
                    | wx.HSCROLL
                    | wx.TE_RICH2
            )
        )
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Show(True)

    def OnClose(self, event):
        """Close the window. But it is not closed."""
        self.parent.viewm.Check(ID_OUTPUT, False)
        self.Show(False)
        self.parent.OnTile(event)
