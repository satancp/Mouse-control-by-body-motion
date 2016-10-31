from Tkinter import *
from Process import Process
from PIL import Image, ImageTk
from Control import Control
import cv2
import time
import thread

class Main(object):

    def __init__(self):
        self.processor = Process()
        self.control = Control()
        self.width = 800   
        self.height = 600
        self.fps = 1000 / 60
        self.UI_handler = []

    def start(self):
        self.root = Tk()
        self.root.title("Motion Control")
        self.canvas = Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack()
        self.timerEventListener()
        self.root.mainloop()
        self.closeEvent()

    def timerEventListener(self):
        if (self.fps == None):
            return 
        self.timerEvent()
        self.refreshUI()
        self.canvas.after(self.fps, self.timerEventListener)      

    def timerEvent(self):
        self.processor.process()

    def closeEvent(self):
        self.processor.close()

    def drawRealtimeImages(self):
        for handle in self.UI_handler:
            self.canvas.delete(handle)
        self.UI_handler = []
        view = Process.BGRtoRGBA(self.processor.original_image, self.width / 2, self.height / 2)
        self.view1 = ImageTk.PhotoImage(image=Image.fromarray(view))
        self.processor.paint()
        view = Process.BGRtoRGBA(self.processor.drawing_canvas, self.width / 2, self.height / 2)
        self.view2 = ImageTk.PhotoImage(image=Image.fromarray(view))
        view = Process.GRAYtoRGBA(self.processor.thresholded_image, self.width / 2, self.height / 2)
        self.view3 = ImageTk.PhotoImage(image=Image.fromarray(view))
        self.UI_handler.append(self.canvas.create_image(0, 0, image=self.view1, anchor="nw"))
        self.UI_handler.append(self.canvas.create_image(800, 600, image=self.view2, anchor="se"))
        self.UI_handler.append(self.canvas.create_image(0, 600, image=self.view3, anchor="sw"))
        if hasattr(self.processor, 'defect_point') and len(self.processor.defect_point) != 0 :
            self.UI_handler.append(self.canvas.create_text(750, 20, text="Fingers: " + str(len(self.processor.defect_point) - 2), anchor="ne", font="15"))
        else :
            self.UI_handler.append(self.canvas.create_text(750, 20, text="Fingers: " + str(0), anchor="ne", font="15"))
        if self.control.signal == True :
            self.UI_handler.append(self.canvas.create_text(750, 40, text="Control Mode: On", anchor="ne", font="15"))
        else :
            self.UI_handler.append(self.canvas.create_text(750, 40, text="Control Mode: Off", anchor="ne", font="15"))
        
    def refreshUI(self):
        self.drawRealtimeImages()
        if hasattr(self.processor, 'defect_point') :
            self.control.gestureAnalysis(self.processor.defect_point,self.processor.center)

Main().start()
