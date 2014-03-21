#####################
## Animation Class (Slightly Modified)
## Written by Professor Kosbie
## Carnegie Mellon University
## www.kosbie.net/cmu/fall-12/15-112/handouts/AnimationWithClasses/Animation.py
########################

import random
from Tkinter import *
import tkMessageBox

###########################################
# Animation class
###########################################

class Animation(object):
    # Animation method definitions
    def mouseMotion(self, event): pass
    def leftMousePressed(self, event): pass
    def leftMouseMoved(self, event): pass
    def leftMouseReleased(self, event): pass
    def rightMousePressed(self, event): pass
    def rightMouseMoved(self, event): pass
    def rightMouseReleased(self, event): pass
    def keyPressed(self, event): pass
    def timerFired(self): pass
    def init(self): pass
    def redrawAll(self): pass

    # Call app.run(width,height) to get your app started
    def run(self):
        # create the root and the canvas
        self.root = Tk()
        self.root.wm_title(self.appTitle)
        if (self.fullscreen == True):
            self.width, self.height = self.root.winfo_screenwidth(),\
            self.root.winfo_screenheight()
            self.root.overrideredirect(True)
            self.root.geometry("%dx%d+0+0" % (self.width, self.height))
            self.root.focus_set() # <-- move focus to this widget
        if (self.resizable == False):
            self.root.resizable(width=FALSE, height=FALSE)
        #t=FadeToplevel(self.root)
        #t.fade_in()
        self.canvas = Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack()
        # set up events
        def redrawAllWrapper():
            self.canvas.delete(ALL)
            self.redrawAll()
        def mouseMotionWrapper(event):
            self.mouseMotion(event)
            #redrawAllWrapper()
        def leftMousePressedWrapper(event):
            self.leftMousePressed(event)
            #redrawAllWrapper()
        def leftMouseMovedWrapper(event):
            self.leftMouseMoved(event)
            #redrawAllWrapper()
        def leftMouseReleasedWrapper(event):
            self.leftMouseReleased(event)
            #redrawAllWrapper()
        def rightMousePressedWrapper(event):
            self.rightMousePressed(event)
            #redrawAllWrapper()
        def rightMouseMovedWrapper(event):
            self.rightMouseMoved(event)
            #redrawAllWrapper()
        def rightMouseReleasedWrapper(event):
            self.rightMouseReleased(event)
            #redrawAllWrapper()
        def keyPressedWrapper(event):
            self.keyPressed(event)
            #redrawAllWrapper()
        def callback():
            if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
                self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", callback)
        self.root.bind("<Key>", keyPressedWrapper)
        self.root.bind("<Button-1>", leftMousePressedWrapper)
        self.root.bind("<Button-3>", rightMousePressedWrapper)
        self.canvas.bind("<Motion>", mouseMotionWrapper)
        self.canvas.bind("<B1-Motion>", leftMouseMovedWrapper)
        self.canvas.bind("<B3-Motion>", rightMouseMovedWrapper)
        self.root.bind("<B1-ButtonRelease>", leftMouseReleasedWrapper)
        self.root.bind("<B3-ButtonRelease>", rightMouseReleasedWrapper)
        # set up timerFired events
        def timerFiredWrapper():
            self.timerFired()
            if(self.refreshOn == True):
                redrawAllWrapper()
            # pause, then call timerFired again
            self.canvas.after(self.timerFiredDelay, timerFiredWrapper)
        # init and get timerFired running
        self.init()
        timerFiredWrapper()
        # and launch the app
        self.root.mainloop()

class FadeToplevel(Toplevel):
    '''A toplevel widget with the ability to fade in'''
    def __init__(self, *args, **kwargs):
        Toplevel.__init__(self, *args, **kwargs)
        self.attributes("-alpha", 0.0)

    def fade_in(self):
        alpha = self.attributes("-alpha")
        alpha = min(alpha + .01, 1.0)
        self.attributes("-alpha", alpha)
        if alpha < 1.0:
            self.after(10, self.fade_in)
