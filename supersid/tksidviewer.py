"""
tkSidViewer class implements a graphical user interface for SID based on tkinter
"""
from __future__ import print_function
import matplotlib
# matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

# handle both Python 2 and 3
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk
import tkMessageBox

import supersid_plot as SSP
from config import FILTERED, RAW

class tkSidViewer():
    '''
    Create the Tkinter GUI
    '''
    def __init__(self, controller):
        """SuperSID Viewer using Tkinter GUI for standalone and client.
        Creation of the Frame with menu and graph display using matplotlib
        """
        matplotlib.use('TkAgg')
        self.version = "1.3.2 20150421 (tk)"
        self.controller = controller  # previously referred as 'parent'
        self.tk_root = tk.Tk()
        self.tk_root.title("supersid @ " + self.controller.config['site_name'])

        # All Menus creation
        menubar = tk.Menu(self.tk_root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save Raw buffers", command=lambda: self.save_file('r'),underline=5,accelerator="Ctrl+R")
        filemenu.add_command(label="Save Filtered buffers", command=lambda: self.save_file('f'),underline=5,accelerator="Ctrl+F")
        filemenu.add_command(label="Save Extended raw buffers", command=lambda: self.save_file('f'),underline=5,accelerator="Ctrl+E")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.close,underline=1,accelerator="Ctrl+X")
        self.tk_root.bind_all("<Control-r>", self.save_file)
        self.tk_root.bind_all("<Control-f>", self.save_file)
        self.tk_root.bind_all("<Control-e>", self.save_file)
        self.tk_root.bind_all("<Control-x>", self.close)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About...", command=self.on_about)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.tk_root.config(menu=menubar)

        # FigureCanvas
        self.psd_figure = Figure(facecolor='beige')
        self.canvas = FigureCanvas(self.psd_figure, master=self.tk_root)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.toolbar = NavigationToolbar2TkAgg( self.canvas, self.tk_root)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.axes = self.psd_figure.add_subplot(111)
        self.axes.hold(False)

        # StatusBar
        self.statusbar_txt = tk.StringVar()
        self.label=tk.Label(self.tk_root, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                           textvariable=self.statusbar_txt,
                           font=('arial',12,'normal'))
        self.statusbar_txt.set('Initialization...')
        self.label.pack(fill=tk.X)

    def run(self):
        self.need_refresh = False
        self.refresh_psd() # start the re-draw loop
        self.tk_root.mainloop()

    def close(self, param=None):
        self.tk_root.quit()

    def status_display(self, message, level=0, field=0):
        """update the main frame by changing the message in status bar"""
        #print(message)
        self.statusbar_txt.set(message)

    def get_psd(self, data, NFFT, FS):
        """By calling 'psd' within axes, it both calculates and plots the spectrum"""
        Pxx, freqs = self.axes.psd(data, NFFT = NFFT, Fs = FS)
        self.need_refresh = True
        return Pxx, freqs

    def refresh_psd(self, z=None):
        """redraw the graphic PSD plot if needed i.e.new data have been given to get_psd"""
        if self.need_refresh:
            self.canvas.draw()
            self.need_refresh = False
        self.tk_root.after(500, self.refresh_psd)

    def save_file(self, param=None):
        """Save the files as per user's menu choice"""
        param = param if isinstance(param, str) else param.keysym # which is the letter with the CTRL-
        if param == 'r':
            saved_files = self.controller.save_current_buffers(log_type='raw', log_format = 'both')
        elif param == 'f':
            saved_files = self.controller.save_current_buffers(log_type='filtered', log_format = 'both')
        elif param == 'e':
            saved_files = self.controller.save_current_buffers(log_type='raw', log_format = 'supersid_extended')
        tkMessageBox.showinfo("SuperSID files saved", "\n".join(saved_files))

    def on_about(self):
        """About message box display"""
        tkMessageBox.showinfo("SuperSID", self.controller.about_app())

