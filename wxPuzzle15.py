#! /usr/bin/env python2.7

from __future__ import print_function
import wx
import puzzle15
import sys



class TilePanel(wx.Panel):

  def __init__(self, label, bkgrd='Green', size=(70, 70), parent=None, ID=-1):
    """Initializes the tile panel."""
    wx.Panel.__init__(self, parent, ID, wx.DefaultPosition, size, wx.RAISED_BORDER, label)
    self.label = label
    self.SetBackgroundColour(bkgrd)
    self.SetMinSize(size)
    self.Bind(wx.EVT_PAINT, self.OnPaint)


  def OnPaint(self, event):
    """On Paint event handler."""
    sz = self.GetClientSize()
    dc = wx.PaintDC(self)
    w, h = dc.GetTextExtent(self.label)
    dc.SetFont(self.GetFont())
    dc.DrawText(self.label, (sz.width - w) // 2, (sz.height - h) // 2)



class BoardFrame(wx.Frame):
  
  def __init__(self, pzlType='Puzzle 15', pos=wx.DefaultPosition):
    wx.Frame.__init__(self, None, -1, pzlType, pos)
    # check puzzle type
    if pzlType == 'Puzzle 15':
      self.size = 4
    elif pzlType == 'Puzzle 8':
      self.size = 3
    elif pzlType == 'Puzzle 3':
      self.size = 2
    else:
      raise ValueError('Invalid puzzle')
    # add a statusbar
    self.statusbar = self.CreateStatusBar()
    self.statusbar.SetFieldsCount(2)
    # add a toolbar
    self.toolbar = self.CreateToolBar()
    img = wx.Image('shuffle.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
    self.SHUFFLE_ID = 1
    item = self.toolbar.AddSimpleTool(self.SHUFFLE_ID, img, 'Shuffle')
    self.Bind(wx.EVT_MENU, self.OnShuffle, item)
    img = wx.Image('solve.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
    self.SOLVE_ID = 2
    item = self.toolbar.AddSimpleTool(self.SOLVE_ID, img, 'Solve')
    self.Bind(wx.EVT_MENU, self.OnSolve, item)
    self.toolbar.Realize()
    # add the board
    self.sizer = wx.GridSizer(rows=self.size, cols=self.size, hgap=5, vgap=5)
    self.FillBoard()
    self.SetSizerAndFit(self.sizer)
    self.SetMinSize(self.GetClientSize())
    self.SetMaxSize((500, 500))
    # event binding
    self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyDown)


  def Swap(self, loc, layout=True):
    """Swap the cell in location with the empty cell."""
    # detach the cell to swap and the empty cell
    self.sizer.Detach(loc)
    self.sizer.Detach(self.empty - 1 if loc < self.empty else self.empty)
    # find the reference of the cell to swap
    item = self.FindWindowByName(str(self.board[loc]))
    # insert a new empty cell and move the cell to swap
    if loc < self.empty:
      self.sizer.InsertStretchSpacer(loc)
      self.sizer.Insert(self.empty, item, flag=wx.EXPAND)
    else:
      self.sizer.Insert(self.empty, item, flag=wx.EXPAND)
      self.sizer.InsertStretchSpacer(loc)
    # update the board
    self.board[self.empty], self.board[loc] = self.board[loc], self.board[self.empty]
    self.moves += 1
    # update tile color
    if self.board[int(item.GetName()) - 1] == int(item.GetName()):
      item.SetBackgroundColour('Green')
    else:
      item.SetBackgroundColour('Red')
    # update the empty cell location and the layout
    self.empty = loc
    if layout:
      self.sizer.Layout()
    self.UpdateStatusBar()

  def UpdateStatusBar(self):
    self.statusbar.SetStatusText('Moves: {}'.format(self.moves), 0)
    # compute the number of misplaced tiles
    left = len([v for i, v in enumerate(self.board) if v != i+1 and v != len(self.board)])
    self.statusbar.SetStatusText('Tiles left: {}'.format(left), 1)

  def ClearBoard(self):
    """Remove all the tiles."""
    self.sizer.Clear()
    for child in self.GetChildren():
      if isinstance(child, TilePanel):
        child.Destroy()

  def FillBoard(self):
    """Fill the board with a random and solvable configuration."""
    # add properties
    self.board = puzzle15.spuzzle(self.size)
    self.empty = self.board.index(len(self.board))
    self.moves = 0
    # add tiles
    for i, v in enumerate(self.board):
      if v == len(self.board):
        self.sizer.AddStretchSpacer()
      else:
        background = 'Green' if v == i+1 else 'Red'
        tile = TilePanel(parent=self, label=str(v), bkgrd=background)
        self.sizer.Add(tile, flag=wx.EXPAND)
    self.sizer.Layout()
    self.UpdateStatusBar()

  def EnableToolbar(self):
    """Enable toolbar items."""
    self.toolbar.EnableTool(self.SHUFFLE_ID, True)
    self.toolbar.EnableTool(self.SOLVE_ID, True)


  def OnKeyDown(self, event):
    """Key down event handler."""
    # get the key code
    keycode = event.GetKeyCode()
    # check which arrow has been pressed and swap cells
    if keycode == wx.WXK_LEFT and (self.empty % self.size) + 1 < self.size:
        self.Swap(self.empty + 1)
    elif keycode == wx.WXK_RIGHT and (self.empty % self.size) - 1 >= 0:
        self.Swap(self.empty - 1)
    elif keycode == wx.WXK_UP and (self.empty + self.size) < len(self.board):
        self.Swap(self.empty + self.size)
    elif keycode == wx.WXK_DOWN and (self.empty - self.size) >= 0:
        self.Swap(self.empty - self.size)
    else:
      event.Skip()

  def OnShuffle(self, event):
    """Shuffle the board."""
    self.ClearBoard()
    self.FillBoard()
    # set the focus (to any tile) in order to use arrow keys
    item = self.FindWindowByName('1')
    item.SetFocus()

  def OnSolve(self, event):
    """Solve the puzzle."""
    # get the first solution
    steps = puzzle15.solve(self.board, lowerBound=-1)
    # check if the puzzle can be solved
    if steps:
      time = 10
      elapsed = time + 250 * len(steps)
      # disable toolbar while solving
      self.toolbar.EnableTool(self.SHUFFLE_ID, False)
      self.toolbar.EnableTool(self.SOLVE_ID, False)
      # simulate animation
      for loc in [x for x, y in steps]:
        wx.CallLater(time, self.Swap, loc)
        time += 250
      # enable toolbar items after simulation
      wx.CallLater(elapsed, self.EnableToolbar)



class PuzzleApp(wx.App):

  def __init__(self, pzlType='Puzzle 15'):
    """Initializes the application."""
    self.pzlType = pzlType
    wx.App.__init__(self)
    

  def OnInit(self):
    self.frame = BoardFrame(pzlType=self.pzlType)
    self.frame.Show()
    self.SetTopWindow(self.frame)
    return True





if __name__ == '__main__':
  if len(sys.argv) == 2:
    app = PuzzleApp(pzlType='Puzzle ' + sys.argv[1])
  else:
    app = PuzzleApp()
  app.MainLoop()