"""PyCoder - A Python File Editor

Author: Zhang Haoran; Zhou Yangqi; Su Chuyao
Datetime: 2020/3/9
Version: 4.3.2"""

__version__ = '4.3.2'

# imports
from wx.stc import StyledTextCtrl as wxSTC
from wx.html2 import *
from wx.stc import *
from tools.output import OutputWindow, ID_OUTPUT
from tools.filechoose import FileChooseWindow, ID_FILE_CHOOSER
from tools.guide import GuideWindow, ID_GUIDE
from tools.console import ConsoleWindow, ID_CONSOLE
from tools.jsonedit import JSONWindow, ID_JSON_EDIT
import builtins
import keyword
import sys
import threading
import traceback
import wx

# IDs
NAME = 'PyCoder'
ID_RUN = 10000
ID_DEBUG = 10001
ID_AUTO_COMP = 10002
ID_OUTPUTS = 10025
ID_FILE = 10005
ID_HELP = 10010
ID_MAIN = 10011
ID_TILABLE = 10006
ID_STOP_RUNNING = 10007
ID_CLEAR_OUTPUT = 10008
ID_CREATABLE = 10009
ID_ABOUT = 10014
ID_CLEAR_WR = 10015
ID_INSERT = 10016
ID_INS_SUPER = 10017
ID_INS_MAIN = 10018
ID_INS_FUNC = 10019
ID_INS_CLASS = 10020
ID_HTML = 10030


# classes
class Callable(object):
    """Callable object"""

    def __init__(self, call, *args, **kwargs):
        """Callable(callable, ...) -> Callable

        This is an object which is callable.

        Example:
        >>> c = Callable(print, 3, 4, True, 'The')
        >>> c()
        3 4 True The
        """
        self.call = call
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        """Call self.call with self.args, self.kwargs and args, kwargs."""
        return self.call.__call__(*args, *self.args, **kwargs, **self.kwargs)


class CodeEditCtrl(wxSTC):
    """CodeEditCtrl(text, style, parent=None) -> wx.stc.StyledTextCtrl

    This object is one of the children of wx.stc.StyledTextCtrl. It can show us a TextCtrl but colorful."""

    fontdata = {
        'name': 'Consolas',
        'size': 16
    }
    keyw = keyword.kwlist
    funw = dir(builtins)
    funw.append('self')
    funw.append('cls')

    def __init__(self, text, style=STC_STYLE_DEFAULT, parent=None):
        """CodeEditCtrl(text, style=STC_STYLE_DEFAULT, parent=None) -> wx.stc.StyledTextCtrl"""
        super(CodeEditCtrl, self).__init__(parent, style=style)
        self.SetupSTC()
        self.AddText(text)

    def SetupSTC(self):
        """Setup the wxSTC

        This method carries out the work of setting up the demo editor.
        It's separate so as not to clutter up the init code.
        """
        self.SetLexer(STC_LEX_PYTHON)
        self.SetKeyWords(0, ' '.join(self.keyw))  # keywords
        self.SetKeyWords(1, ' '.join(self.funw))  # built-in-function-or-methods
        self.SetProperty('fold', '1')
        self.SetProperty('tab.timmy.whinge.level', '1')  # Set left and right margins
        self.SetMargins(2, 2)
        self.SetMarginType(1, STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 60)
        self.SetIndent(4)
        self.SetIndentationGuides(True)
        self.SetBackSpaceUnIndents(True)
        self.SetTabIndents(True)
        self.SetTabWidth(4)
        self.SetUseTabs(False)
        self.SetupFont()
        self.SetViewWhiteSpace(False)
        self.SetEOLMode(STC_EOL_LF)
        self.SetViewEOL(False)
        self.SetEdgeMode(STC_EDGE_NONE)

    def SetupFont(self):
        """Setup the font."""
        self.StyleSetSpec(STC_STYLE_DEFAULT, 'fore:#000000,back:#FFFFFF,face:%s,size:%s' % (
            self.fontdata['name'],
            self.fontdata['size']))
        self.StyleClearAll()
        self.StyleSetSpec(STC_P_DEFAULT, 'fore:#000000,back:#FFFFFF,face:%s,size:%s' % (
            self.fontdata['name'],
            self.fontdata['size']))
        self.StyleSetSpec(STC_P_COMMENTLINE, 'fore:#7F7F7F,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_NUMBER, 'fore:#7F0000,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_STRING, 'fore:#007F00,bold,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_CHARACTER, 'fore:#007F00,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_WORD, 'fore:#00007F,bold,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_WORD2, 'fore:#7F007F,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_TRIPLE, 'fore:#7F7F7F,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_TRIPLEDOUBLE, 'fore:#7F7F7F,bold,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_CLASSNAME, 'fore:#007F7F,bold,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_DEFNAME, 'fore:#007F7F,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_DECORATOR, 'fore:#7F7F00,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_OPERATOR, 'fore:#000000,bold,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_IDENTIFIER, 'fore:#000000,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_COMMENTBLOCK, 'fore:#7F7F7F,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_STRINGEOL, 'fore:#FFFFFF,back:#000000,eol,face:%s,size:%s' % (
            self.fontdata['name'],
            self.fontdata['size']
        ))


class EditWindow(wx.MDIChildFrame):
    """EditWindow object"""
    saved = False
    state = ID_FILE
    messages = {
        'not-saved': 'Source is not saved. OK to save?'
    }

    def __init__(self, parent=None, file='', code=''):
        """EditWindow(parent=None, file='', code='') -> wx.Frame

        Create a new editor for editing Python files.
        """
        super(EditWindow, self).__init__(parent, title=file, style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.code = CodeEditCtrl(code, parent=self)
        self.code.Bind(EVT_STC_KEY, self.OnAutoComp)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Show(True)

    def OnAutoComp(self, event):
        """Automatic completion."""
        self.saved = False
        if self.parent.autocomp:
            pass

    def OnClose(self, event):
        """Check if the file was saved, if not, it would ask the user save or not."""
        if self.saved:
            self.Destroy()
        else:
            savable = wx.MessageBox(
                self.messages['not-saved'],
                self.GetTitle(), style=wx.YES_NO | wx.CENTRE
            )
            if savable:
                self.parent.OnSave(event)
        self.parent.OnTile(event)


class HtmlWindow(wx.MDIChildFrame):
    """HtmlWindow object

    Create a html window with no button."""
    title = 'Html View - [%s]'
    state = ID_HTML

    def __init__(self, parent=None, file='', code=''):
        """HtmlWindow(parent=None, file='', code='') -> wx.MDIChildFrame"""
        super(HtmlWindow, self).__init__(
            parent,
            title=self.title % file,
            style=wx.DEFAULT_FRAME_STYLE
        )
        self.parent = parent
        self.show = WebView.New(self)
        self.show.SetPage(code, file)
        self.Show(True)

    def OnClose(self, event):
        """Close the window by destroying."""
        self.Destroy()
        self.parent.OnTile(event)


class AboutWindow(wx.Dialog):
    """AboutWindow object"""
    title = 'About'
    state = ID_ABOUT
    messages = {
        'about': 'There is not anything to show. This product does not have any copyrights.'
    }

    def __init__(self, parent=None):
        """AboutWindow(parent=None) -> wx.Dialog"""
        super(AboutWindow, self).__init__(parent, title=self.title, style=wx.DEFAULT_FRAME_STYLE)
        self.message = wx.StaticText(self, label=self.messages['about'])
        self.ok = wx.Button(self, label='OK')
        self.ok.Bind(wx.EVT_BUTTON, self.OnClose)
        self.ver = wx.BoxSizer(wx.VERTICAL)
        self.ver.Add(self.message, proportion=1, flag=wx.ALIGN_CENTER | wx.ALL, border=0)
        self.ver.Add(self.ok, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=0)
        self.SetSizer(self.ver)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        """Close the window by destroying."""
        self.Destroy()


class MainWindow(wx.MDIParentFrame):
    """MainWindow object"""
    title = 'PyCoder'
    statext = 'Welcome to PyCoder Editor! Press F5 to run code.'
    default = '# -*- coding: utf-8 -*-\n'
    size = (0, 0)  # real value unknown
    icosize = (24, 24)
    autocomp = False
    tilable = False
    noname = 'untitled'
    thread = None
    clearable = False
    creatable = False
    file = None
    messages = {
        'save-failed': 'Save file failed.',
        'window-not-found': 'You must select a sub-window first.',
        'thread-not-found': 'You must start a thread running or debugging first.',
        'open-failed': 'Open file failed.',
        'select-error': 'You must open a file and select it first.'
    }
    exprs = {
        'main': 'if __name__ == "__main__":\n%s',
        'super': 'super(%s).__init__(%s)',
        'func': 'def %s(%s):\n%s',
    }
    toolmsgs = {
        'exit': 'Exit the program.',
        'new': 'Create a new file for coding.',
        'open': 'Open a file from the computer.',
        'save': 'Save the editing file.',
        'save-as': 'Resave the editing file.',
        'run': 'Run the code directly.'
    }
    filetypes = {
        'py': ['.py', '.pyw', '.pyc', '.pyi', '.pyd', '.pyz', '.spec'],
        'xml': ['.xml', '.xrc', '.htm', '.html', '.shtml'],
        'img': ['.png', '.jpg', '.jpeg', '.bmp', '.ico', '.icns'],
        'cpp': ['.cpp', '.h'],
        'exe': ['.exe'],
        'txt': ['.txt', '.ini', '.css', '.json', '.log'],
        'cmd': ['.cmd', '.bat'],
        'lnk': ['.url', '.lnk']
    }
    state = ID_MAIN

    def __init__(self, parent=None):
        """MainWindow(parent=None) -> wx.Frame

        The basest window.
        """
        super(MainWindow, self).__init__(
            parent,  # default is None
            title=self.title,  # default is ''
            pos=(0, 0),  # default is unknown
            size=wx.GetDisplaySize(),  # default is 1920x1080
            style=wx.DEFAULT_FRAME_STYLE  # default is this
        )
        self.BindEvents()
        self.CreateMenu()
        self.SetMenuBar(self.menubar)
        self.CreateTool()
        self.SetToolBar(self.toolbar)
        self.CreateStatus()
        self.SetStatusBar(self.statusbar)
        self.output = OutputWindow(self)
        self.chooser = FileChooseWindow(self)
        self.guide = GuideWindow(self)
        self.console = ConsoleWindow(self)
        self.jsonedit = JSONWindow(self)
        self.SetAutoLayout(True)
        self.Show(True)
        self.Tile(wx.VERTICAL)

    def OnNew(self, event):
        """Create a new code area."""
        self.AddCodeArea(self.noname, self.default)
        self.OnTile(event)

    def OnOpen(self, event):
        """Open a source or a file."""
        dialog = wx.FileDialog(self, 'Open File', style=wx.ID_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            file = dialog.GetPath()
            try:
                code = self.OpenFile(file)
                self.AddCodeArea(file, code)
            except (FileNotFoundError, UnicodeDecodeError, SyntaxError):
                wx.MessageBox(self.messages['open-failed'], self.title)
        dialog.Destroy()
        self.OnTile(event)

    def OnSave(self, event):
        """Save a file. If the file was untitled it will redirect to save-as."""
        area = self.GetActiveChild()
        if area and area.state == ID_FILE:
            file = area.GetTitle()
            if file == self.noname:
                self.OnSaveAs(event, True)
            else:
                code = area.code.GetValue()
                try:
                    self.SaveFile(file, code)
                    area.saved = True
                except (FileNotFoundError, UnicodeDecodeError, SyntaxError):
                    wx.MessageBox(self.messages['save-failed'], self.title)
            self.OnTile(event)
        else:
            wx.MessageBox(self.messages['select-error'], self.title)

    def OnSaveAs(self, event, restate=False):
        """Save the source in a new file."""
        area = self.GetActiveChild()
        if area and area.state == ID_FILE:
            default = area.GetTitle()
            code = area.code.GetValue()
            dialog = wx.FileDialog(self, 'Save As...', defaultFile=default, style=wx.ID_NEW)
            if dialog.ShowModal() == wx.ID_OK:
                file = dialog.GetPath()
                try:
                    self.SaveFile(file, code)
                    if restate:
                        area.SetTitle(file)
                        area.saved = True
                except (FileNotFoundError, UnicodeDecodeError, SyntaxError):
                    wx.MessageBox(self.messages['save-failed'], self.title)
            dialog.Destroy()
            self.OnTile(event)
        else:
            wx.MessageBox(self.messages['select-error'], self.title)

    def OnClose(self, event):
        """Close the child window."""
        area = self.GetActiveChild()
        if area:
            area.Close()
            self.OnTile(event)
        else:
            wx.MessageBox(self.messages['window-not-found'], self.title)

    def OnExit(self, event):
        """Close the window."""
        app.ExitMainLoop()
        self.Destroy()

    def OnRun(self, event):
        """Run the source. If self.creatable, it would create a new thread."""
        area = self.GetActiveChild()
        if area and area.state == ID_FILE:
            file = area.GetTitle()
            code = area.code.GetValue()
            if self.InObject(file, *self.filetypes['xml']):
                self.AddHtmlArea(file, code)
            else:
                if self.creatable:
                    self.thread = threading.Thread(target=self.RunCode, args=(file, code))
                    self.thread.setDaemon(True)
                    self.thread.start()
                else:
                    self.RunCode(file, code)
        else:
            wx.MessageBox(self.messages['select-error'], self.title)

    def OnDebug(self, event):
        """Debug the code.

        If the code has a error, the debugger will popup a wx.MessageBox to show the detail."""
        area = self.GetActiveChild()
        if area and area.state == ID_FILE:
            file = area.GetTitle()
            code = area.code.GetValue()
            if self.creatable:
                self.thread = threading.Thread(target=self.DebugCode, args=(file, code))
                self.thread.setDaemon(True)
                self.thread.start()
            else:
                self.DebugCode(file, code)
        else:
            wx.MessageBox(self.messages['select-error'], self.title)

    def OnStopRunning(self, event):
        """Stop running a file."""
        if self.thread:
            self.thread.join()
            self.output.output.AppendText('[Finished Code]\n')
        else:
            wx.MessageBox(self.messages['thread-not-found'], self.title)

    def OnClearOutput(self, event):
        """Clear the output."""
        self.output.output.SetValue(wx.EmptyString)

    def OnSetClearable(self, event):
        self.clearable = event.IsChecked()

    def OnInsSuper(self, event):
        pass

    def OnInsMain(self, event):
        """Insert a main expr."""
        self.TextCmd(
            'InsertText',
            True,
            self.TextCmd('GetInsertionPoint', False),
            self.exprs['main'] % '    '
        )

    def OnInsFunc(self, event):
        pass

    def OnInsClass(self, event):
        pass

    def OnSetAutoComp(self, event):
        self.autocomp = event.IsChecked()

    def OnSetCreatable(self, event):
        self.creatable = event.IsChecked()

    def OnUndo(self, event):
        self.TextCmd('Undo')

    def OnRedo(self, event):
        self.TextCmd('Redo')

    def OnCut(self, event):
        self.TextCmd('Cut')

    def OnCopy(self, event):
        self.TextCmd('Copy')

    def OnPaste(self, event):
        self.TextCmd('Paste')

    def OnDelete(self, event):
        self.TextCmd('DeleteBack')

    def OnSelectAll(self, event):
        self.TextCmd('SelectAll')

    def OnSetOutput(self, event):
        self.output.Show(event.IsChecked())

    def OnSetChooser(self, event):
        self.chooser.Show(event.IsChecked())

    def OnSetGuide(self, event):
        self.guide.Show(event.IsChecked())

    def OnSetConsole(self, event):
        self.console.Show(event.IsChecked())

    def OnSetJSONEdit(self, event):
        self.jsonedit.Show(event.IsChecked())

    def OnSetTilable(self, event):
        """Set the tilable of the window."""
        self.tilable = event.IsChecked()

    def OnTile(self, event):
        """Tile the window."""
        self.Tile(wx.VERTICAL) if self.tilable else None

    def OnHelp(self, event):
        """Make a help window."""
        doc = self.OpenFile('help.html')
        win = HtmlWindow(self, 'help.html', doc)
        win.Activate()

    def OnAbout(self, event):
        """Make an about window."""
        dialog = AboutWindow(self)
        dialog.ShowModal()

    def CreateMenu(self):
        """Create a menubar that has some menus."""
        self.filem = wx.Menu()
        self.filem.Append(wx.ID_NEW)
        self.filem.Append(wx.ID_OPEN)
        self.filem.Append(wx.ID_SAVE)
        self.filem.Append(wx.ID_SAVEAS)
        self.filem.AppendSeparator()
        self.filem.Append(wx.ID_CLOSE, '&Close\tEsc')
        self.filem.AppendSeparator()
        self.filem.Append(wx.ID_EXIT, '&Exit\tAlt+F4')
        self.codem = wx.Menu()
        self.codem.Append(ID_RUN, '&Run\tF5')
        self.codem.Append(ID_DEBUG, '&Debug')
        self.codem.Append(ID_STOP_RUNNING, '&Stop')
        self.codem.AppendSeparator()
        self.codem.outpm = wx.Menu()
        self.codem.outpm.Append(ID_CLEAR_OUTPUT, '&Clear\tCtrl+Shift+C')
        self.codem.outpm.AppendCheckItem(ID_CLEAR_WR, '&Keep Clear')
        self.codem.Append(ID_OUTPUTS, '&Outputs', self.codem.outpm)
        self.codem.instm = wx.Menu()
        self.codem.instm.Append(ID_INS_MAIN, '&Main Expr\tCtrl+Alt+M')
        self.codem.Append(ID_INSERT, '&Insert', self.codem.instm)
        self.codem.AppendSeparator()
        self.codem.AppendCheckItem(ID_AUTO_COMP, '&Auto Completion')
        self.codem.AppendCheckItem(ID_CREATABLE, '&New Thread')
        self.editm = wx.Menu()
        self.editm.Append(wx.ID_UNDO)
        self.editm.Append(wx.ID_REDO)
        self.editm.AppendSeparator()
        self.editm.Append(wx.ID_CUT)
        self.editm.Append(wx.ID_COPY)
        self.editm.Append(wx.ID_PASTE)
        self.editm.Append(wx.ID_DELETE)
        self.editm.AppendSeparator()
        self.editm.Append(wx.ID_SELECTALL)
        self.viewm = wx.Menu()
        self.viewm.AppendCheckItem(ID_OUTPUT, '&Output')
        self.viewm.AppendCheckItem(ID_FILE_CHOOSER, '&File Chooser')
        self.viewm.AppendCheckItem(ID_GUIDE, '&Guide')
        self.viewm.AppendCheckItem(ID_CONSOLE, '&Python Console')
        self.viewm.AppendCheckItem(ID_JSON_EDIT, '&JSON Editor')
        self.viewm.AppendSeparator()
        self.viewm.AppendCheckItem(ID_TILABLE, '&Auto Tile')
        self.viewm.Check(ID_OUTPUT, True)
        self.viewm.Check(ID_FILE_CHOOSER, True)
        self.helpm = wx.Menu()
        self.helpm.Append(wx.ID_HELP)
        self.helpm.AppendSeparator()
        self.helpm.Append(wx.ID_ABOUT)
        self.menubar = wx.MenuBar()
        self.menubar.Append(self.filem, '&File')
        self.menubar.Append(self.codem, '&Code')
        self.menubar.Append(self.editm, '&Edit')
        self.menubar.Append(self.viewm, '&View')
        self.menubar.Append(self.helpm, '&Help')

    def CreateTool(self):
        """Create a toolbar."""
        self.tbflags = (wx.TB_FLAT
                        | wx.NO_BORDER
                        | wx.TB_HORIZONTAL
                        | wx.TB_DOCKABLE
                        | wx.TB_3DBUTTONS
                        )
        self.exitb = wx.Bitmap('icons\\exit.ico')
        self.newb = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, self.icosize)
        self.openb = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, self.icosize)
        self.saveb = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, self.icosize)
        self.saveasb = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_TOOLBAR, self.icosize)
        self.runb = wx.Bitmap('icons\\run.ico')
        self.toolbar = wx.ToolBar(self, style=self.tbflags)
        self.toolbar.AddTool(wx.ID_EXIT, 'Exit', self.exitb,
                             wx.NullBitmap, wx.ITEM_NORMAL,
                             self.toolmsgs['exit'])
        self.toolbar.AddSeparator()
        self.toolbar.AddTool(wx.ID_NEW, 'New', self.newb,
                             wx.NullBitmap, wx.ITEM_NORMAL,
                             self.toolmsgs['new'])
        self.toolbar.AddTool(wx.ID_OPEN, 'Open', self.openb,
                             wx.NullBitmap, wx.ITEM_NORMAL,
                             self.toolmsgs['open'])
        self.toolbar.AddTool(wx.ID_SAVE, 'Save', self.saveb,
                             wx.NullBitmap, wx.ITEM_NORMAL,
                             self.toolmsgs['save'])
        self.toolbar.AddTool(wx.ID_SAVEAS, 'Save As', self.saveasb,
                             wx.NullBitmap, wx.ITEM_NORMAL,
                             self.toolmsgs['save-as'])
        self.toolbar.AddSeparator()
        self.toolbar.AddTool(ID_RUN, 'Run', self.runb,
                             wx.NullBitmap, wx.ITEM_NORMAL,
                             self.toolmsgs['run'])
        self.toolbar.Realize()

    def CreateStatus(self):
        """Create a statusbar."""
        self.statusbar = wx.StatusBar(self)
        self.statusbar.SetFieldsCount(2)
        self.statusbar.SetStatusWidths([-1, -5])
        self.statusbar.SetStatusText(self.statext, 1)

    def BindEvents(self):
        """Bind the eventtree"""
        self.Bind(wx.EVT_MENU, self.OnNew, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnClose, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnRun, id=ID_RUN)
        self.Bind(wx.EVT_MENU, self.OnDebug, id=ID_DEBUG)
        self.Bind(wx.EVT_MENU, self.OnClearOutput, id=ID_CLEAR_OUTPUT)
        self.Bind(wx.EVT_MENU, self.OnSetClearable, id=ID_CLEAR_WR)
        self.Bind(wx.EVT_MENU, self.OnInsMain, id=ID_INS_MAIN)
        self.Bind(wx.EVT_MENU, self.OnSetAutoComp, id=ID_AUTO_COMP)
        self.Bind(wx.EVT_MENU, self.OnSetCreatable, id=ID_CREATABLE)
        self.Bind(wx.EVT_MENU, self.OnUndo, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU, self.OnRedo, id=wx.ID_REDO)
        self.Bind(wx.EVT_MENU, self.OnCut, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU, self.OnCopy, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU, self.OnPaste, id=wx.ID_PASTE)
        self.Bind(wx.EVT_MENU, self.OnDelete, id=wx.ID_DELETE)
        self.Bind(wx.EVT_MENU, self.OnSelectAll, id=wx.ID_SELECTALL)
        self.Bind(wx.EVT_MENU, self.OnSetOutput, id=ID_OUTPUT)
        self.Bind(wx.EVT_MENU, self.OnSetChooser, id=ID_FILE_CHOOSER)
        self.Bind(wx.EVT_MENU, self.OnSetGuide, id=ID_GUIDE)
        self.Bind(wx.EVT_MENU, self.OnSetConsole, id=ID_CONSOLE)
        self.Bind(wx.EVT_MENU, self.OnSetJSONEdit, id=ID_JSON_EDIT)
        self.Bind(wx.EVT_MENU, self.OnSetTilable, id=ID_TILABLE)
        self.Bind(wx.EVT_MENU, self.OnStopRunning, id=ID_STOP_RUNNING)
        self.Bind(wx.EVT_MENU, self.OnHelp, id=wx.ID_HELP)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_SIZING, self.OnTile)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        # self.Bind(wx.EVT_SIZE, self.OnTile)

    def OpenFile(self, file):
        """Open a file and return the content"""
        f = open(file, 'r', encoding='utf-8')
        content = f.read()
        f.close()
        return content

    def SaveFile(self, file, content=''):
        """Save the file."""
        f = open(file, 'w', encoding='utf-8')
        f.write(content)
        f.close()

    def AddCodeArea(self, file, content='', saved=True):
        """Add a code area."""
        win = EditWindow(self, file, content)
        win.saved = saved
        win.Activate()

    def AddHtmlArea(self, file, content=''):
        """Add a html area."""
        win = HtmlWindow(self, file, content)
        win.Activate()

    def RunCode(self, file, content=''):
        """Run the source."""
        if self.clearable:
            self.output.output.SetValue(wx.EmptyString)
        namespace = {
            '__name__': '__main__',
            '__file__': file,
            'print': self.PrintFunc,
            'input': self.InputFunc
        }
        self.output.output.AppendText('[Started Code]\n')
        try:
            exec(compile(content.encode('utf-8'), file, 'exec'), namespace)
        except BaseException as e:
            exc = ''.join(traceback.format_exception(*sys.exc_info()))
            if type(e) == SyntaxError:
                wx.MessageBox(exc, e.__str__())
            else:
                self.output.output.AppendText(exc)
        self.thread = None
        self.output.output.AppendText('[Finished Code]\n')

    def DebugCode(self, file, content=''):
        """Debug the source."""
        namespace = {
            '__name__': '__main__',
            '__file__': file,
            'print': self.PrintFunc,
            'input': self.InputFunc
        }
        self.output.output.AppendText('[Started Code]\n')
        try:
            exec(compile(content.encode('utf-8'), file, 'exec'), namespace)
        except BaseException as e:
            exc = ''
            for info in dir(e.with_traceback(e.__traceback__)):
                if '__' not in info:
                    exc += '%s: %s\n' % (info, getattr(e, info, None))
            wx.MessageBox(exc, self.title)
        self.thread = None
        self.output.output.AppendText('[Finished Code]\n')

    def TextCmd(self, command='', warn=True, *args, **kwargs):
        """Execute a text command in text ctrl."""
        area = self.GetActiveChild()
        if area and area.state == ID_FILE:
            return getattr(area.code, command, lambda: None)(*args, **kwargs)
        else:
            if warn:
                wx.MessageBox(self.messages['select-error'], self.title)

    def PrintFunc(self, *args, **kwargs):
        """Print something. It use namespace to print."""
        print(*args, **kwargs, file=self.output.output)  # why warning???

    def InputFunc(self, prompt=''):
        """Input a thing that like a function."""
        dialog = wx.TextEntryDialog(self, prompt, self.title)
        if dialog.ShowModal() == wx.ID_OK:
            text = dialog.GetValue()
            return text
        dialog.Destroy()

    def EmptyHandler(self, event):
        """This handler is an empty handler.

        If some project is not finished, it will bind this handler for nothing.
        Do not edit this handler.
        """

    def InObject(self, obj, *args):
        """Check if one of the args is in the object, return True"""
        passible = False
        for item in args:
            if item in obj:
                passible = True
        return passible

    def ObjectIn(self, obj, *args):
        """Check if the object is in one of the args, return True"""
        passible = False
        for item in args:
            if obj in item:
                passible = True
        return passible


if __name__ == '__main__':
    """Is this important? Not yet."""
    try:
        app = wx.App()
        MainWindow()
        app.MainLoop()
    except RuntimeError:
        pass
