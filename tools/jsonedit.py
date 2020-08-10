import wx
import json

ID_JSON_EDIT = 10031


class JSONWindow(wx.MDIChildFrame):
    """JSONWindow object"""
    title = 'JSON Edit'
    state = ID_JSON_EDIT
    messages = {
        'open-file': 'Open File',
        'file-not-found': 'The file name you entered is not a valid file name.',
        'decode-error': 'The code of the file is not a json-like code.'
    }
    keys = ['Key', 'Value']

    def __init__(self, parent):
        """JSONWindow(parent=None) -> wx.MDIChildFrame"""
        super(JSONWindow, self).__init__(parent, title=self.title)
        self.parent = parent
        self.input = wx.ComboBox(self, style=wx.TE_PROCESS_ENTER)
        self.input.Bind(wx.EVT_TEXT_ENTER, self.OnProperty)
        self.ok = wx.Button(self, label='OK')
        self.ok.Bind(wx.EVT_BUTTON, self.OnProperty)
        self.browse = wx.Button(self, label='Browse')
        self.browse.Bind(wx.EVT_BUTTON, self.OnBrowse)
        self.props = wx.ListCtrl(self, style=wx.LC_REPORT)
        for name in self.keys:
            count = self.keys.index(name)
            self.props.InsertColumn(count, name)
        self.hor = wx.BoxSizer(wx.HORIZONTAL)
        self.hor.Add(self.input, proportion=1, flag=wx.EXPAND | wx.ALL, border=0)
        self.hor.Add(self.ok, proportion=0, flag=wx.EXPAND | wx.ALL, border=0)
        self.hor.Add(self.browse, proportion=0, flag=wx.EXPAND | wx.ALL, border=0)
        self.ver = wx.BoxSizer(wx.VERTICAL)
        self.ver.Add(self.hor, proportion=0, flag=wx.EXPAND | wx.ALL)
        self.ver.Add(self.props, proportion=1, flag=wx.EXPAND | wx.ALL, border=0)
        self.SetSizer(self.ver)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Show(False)

    def OnProperty(self, event):
        """Read a json file."""
        file = self.input.GetValue()
        try:
            tent = self.parent.OpenFile(file)
            props = json.loads(tent.encode('utf-8'))
            self.MakeProperty(props)
            self.input.Append(file)
        except (UnicodeDecodeError, FileNotFoundError, SyntaxError):
            wx.MessageBox(self.messages['file-not-found'])
        except json.JSONDecodeError:
            wx.MessageBox(self.messages['decode-error'])

    def OnBrowse(self, event):
        """Open a file and show it."""
        dialog = wx.FileDialog(self, self.messages['open-file'], wildcard='*.json', style=wx.ID_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            file = dialog.GetPath()
            self.input.SetValue(file)
            self.input.Append(file)
        dialog.Destroy()

    def OnClose(self, event):
        """Close the window. But it is not closed."""
        self.parent.viewm.Check(ID_JSON_EDIT, False)
        self.Show(False)
        self.parent.OnTile(event)

    def MakeProperty(self, props):
        """Make the dictionary into the list control."""
        items = props.items()
        self.props.DeleteAllItems()
        for key, value in items:
            index = self.props.InsertItem(self.props.GetItemCount(), key)
            self.props.SetItem(index, 1, repr(value))
