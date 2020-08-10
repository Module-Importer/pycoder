import wx

ID_FILE_CHOOSER = 10004


class FileChooseWindow(wx.MDIChildFrame):
    """File choose window"""
    title = 'File Chooser'
    state = ID_FILE_CHOOSER

    def __init__(self, parent=None):
        """FileChooseWindow(parent=None) -> wx.Frame

        Create a window that provides user to choose a file.
        """
        super(FileChooseWindow, self).__init__(parent, title=self.title, style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.search = wx.ComboBox(self, style=wx.TE_PROCESS_ENTER)
        self.search.Bind(wx.EVT_TEXT_ENTER, self.OnExpand)
        self.chooser = wx.GenericDirCtrl(self, style=wx.DIRCTRL_EDIT_LABELS)
        self.chooser.Bind(wx.EVT_DIRCTRL_FILEACTIVATED, self.OnOpen)
        self.chooser.Bind(wx.EVT_DIRCTRL_SELECTIONCHANGED, self.OnUpdate)
        self.ver = wx.BoxSizer(wx.VERTICAL)
        self.ver.Add(self.search, proportion=0, flag=wx.EXPAND | wx.ALL, border=0)
        self.ver.Add(self.chooser, proportion=1, flag=wx.EXPAND | wx.ALL, border=0)
        self.SetSizer(self.ver)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Show(True)

    def OnOpen(self, event):
        """The user double-click the file and create a new area."""
        file = self.chooser.GetPath()
        try:
            code = self.parent.OpenFile(file)
            self.parent.AddCodeArea(file, code)
        except (FileNotFoundError, UnicodeDecodeError, SyntaxError):
            wx.MessageBox(self.parent.messages['open-failed'], self.title)
        self.parent.OnTile(event)

    def OnExpand(self, event):
        """Expand the selection path."""
        path = self.search.GetValue()
        if path not in self.search.GetItems():
            self.search.Append(path)
        self.SetTitle('%s [%s]' % (self.title, path))
        self.chooser.SetPath(path)

    def OnUpdate(self, event):
        """Update the input text."""
        path = self.chooser.GetPath()
        if path not in self.search.GetItems():
            self.search.Append(path)
        self.SetTitle('%s [%s]' % (self.title, path))
        self.search.SetValue(path)

    def OnClose(self, event):
        """Close the window. But it is not closed."""
        self.parent.viewm.Check(ID_FILE_CHOOSER, False)
        self.Show(False)
        self.parent.OnTile(event)
