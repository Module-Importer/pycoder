import wx
import sys

ID_GUIDE = 10012


class GuideWindow(wx.MDIChildFrame):
    """MainWindow object"""
    title = 'Module Importer 2'
    state = ID_GUIDE
    ctrl_size = (0, 0)  # real value unknown
    modules = sys.modules
    module_list = list(sys.modules)
    module = None
    tooltips = {
        'searchin': 'type here',
        'listin': 'the importable modules',
        'showin': 'the attributes of the module'
    }

    def __init__(self, parent=None):
        """GuideWindow(parent=None) -> wx.MDIChildFrame"""
        super(GuideWindow, self).__init__(parent, title=self.title, style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.searchin = wx.ComboBox(self, choices=self.module_list)
        self.searchin.SetToolTip(self.tooltips['searchin'])
        self.searchin.Bind(wx.EVT_TEXT, self.OnSearch)
        self.listin = wx.ListBox(self, size=self.ctrl_size, choices=self.module_list, style=wx.HSCROLL)
        self.listin.SetToolTip(self.tooltips['listin'])
        self.listin.Bind(wx.EVT_LISTBOX_DCLICK, self.OnShowInfo)
        self.listin.Bind(wx.EVT_LISTBOX, self.OnShowDetail)
        self.showin = wx.ListBox(self, size=self.ctrl_size, style=wx.HSCROLL)
        self.showin.SetToolTip(self.tooltips['showin'])
        self.showin.Bind(wx.EVT_LISTBOX_DCLICK, self.OnShowInfo)
        self.hor1 = wx.BoxSizer(wx.HORIZONTAL)
        self.ver = wx.BoxSizer(wx.VERTICAL)
        self.ver.Add(self.searchin, proportion=0, flag=wx.EXPAND | wx.ALL)
        self.ver.Add(self.listin, proportion=1, flag=wx.EXPAND | wx.ALL, border=0)
        self.hor1.Add(self.ver, proportion=1, flag=wx.EXPAND | wx.ALL)
        self.hor1.Add(self.showin, proportion=1, flag=wx.EXPAND | wx.ALL, border=0)
        self.SetSizer(self.hor1)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Show(False)

    def OnSearch(self, event):
        """Detect type and search."""
        typed = self.searchin.GetValue()
        modules = []
        for module in self.module_list:
            if typed in module:  # search
                modules.append(module)
        self.listin.Set(modules)

    def OnShowDetail(self, event):
        """Show the detail of selection module."""
        module = self.listin.GetStringSelection()
        self.module = self.modules[module]
        attrs = dir(self.module)
        self.showin.Set(attrs)

    def OnShowInfo(self, event):
        """Show the information about the selection item."""
        ctrl = event.GetEventObject()
        name = ctrl.GetStringSelection()
        if ctrl == self.listin:
            value = self.module  # that can bind two objects
        else:
            value = getattr(self.module, name, None)
        real = repr(value)  # must be repred
        types = type(value).__name__
        attrs = dir(value)
        docs = value.__doc__
        wx.MessageBox(
            'Name: %s\n'
            'Value: %s\n'
            'Type: %s\n'
            'Attrs: %s\n'
            '\n%s' % (  # these five selects
                name, real, types, attrs, docs
            ),
            caption=self.title
        )

    def OnClose(self, event):
        """Close the window. But it is not closed."""
        self.parent.viewm.Check(ID_GUIDE, False)
        self.Show(False)
        self.parent.OnTile(event)
