import wx
 
class MyForm(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Tutorial")

        panel = wx.Panel(self, wx.ID_ANY)
        
        # Create a menu
        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        
        refreshMenuItem = fileMenu.Append(wx.NewId(), "Refresh",
                                          "Refresh app")
        self.Bind(wx.EVT_MENU, self.onRefresh, refreshMenuItem)
        
        exitMenuItem = fileMenu.Append(wx.NewId(), "E&xit\tCtrl+X", "Exit the program")
        self.Bind(wx.EVT_MENU, self.onExit, exitMenuItem)
        
        menuBar.Append(fileMenu, "File")
        self.SetMenuBar(menuBar)
        
        # Create an accelerator table
        xit_id = wx.NewId()
        yit_id = wx.NewId()
        self.Bind(wx.EVT_MENU, self.onAltX, id=xit_id)
        self.Bind(wx.EVT_MENU, self.onShiftAltY, id=yit_id)
        
        self.accel_tbl = wx.AcceleratorTable(
            [(wx.ACCEL_CTRL, ord('R'), refreshMenuItem.GetId()),
              (wx.ACCEL_ALT, ord('X'), xit_id),
              (wx.ACCEL_SHIFT|wx.ACCEL_ALT, ord('Y'), yit_id)
            ])
        self.SetAcceleratorTable(self.accel_tbl)
        
    #----------------------------------------------------------------------
    def onRefresh(self, event):
        print("refreshed!")
        
    #----------------------------------------------------------------------
    def onAltX(self, event):
        """"""
        print("You pressed ALT+X!")
        
    #----------------------------------------------------------------------
    def onShiftAltY(self, event):
        """"""
        print("You pressed SHIFT+ALT+Y!")
        
    #----------------------------------------------------------------------
    def onExit(self, event):
        """"""
        self.Close()

#----------------------------------------------------------------------
# Run the program
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = MyForm().Show()
    app.MainLoop()