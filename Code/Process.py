import cv2
import os
import random
import numpy as np
import time

class Process(object):

    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.bsModel = cv2.BackgroundSubtractorMOG(20,10,0.5,False)
        self.camera_width = 1280
        self.camera_height = 720
        self.lower_limit = np.array([0, 48, 80], dtype = "uint8")
        self.upper_limit = np.array([20, 255, 255], dtype = "uint8")
        self.black1 = np.array([0, 0, 0], dtype = "uint8")
        self.black2 = np.array([1, 1, 1], dtype = "uint8")
        self.camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.camera_height)
        self.hand_center = []

    def process(self):
        self.readCamera()
        self.readCamera()
        self.thresholding()
        self.retrieveContours()
        if len(self.contours) != 0 :
            self.retrieveHandContour()
            self.findHullDefects()
            self.findHandCenter()
            self.findRealHandCenter()

    def close(self):
        self.camera.release()
        cv2.destroyAllWindows()

    def readCamera(self):
        _, self.original_image = self.camera.read()
        self.original_image = cv2.flip(self.original_image, 1)
        converted_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2HSV)
        skin_mask = cv2.inRange(converted_image, self.lower_limit, self.upper_limit)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        skin_mask = cv2.erode(skin_mask, kernel, iterations = 2)
        skin_mask = cv2.dilate(skin_mask, kernel, iterations = 2)
        skin_mask = cv2.GaussianBlur(skin_mask, (3, 3), 0)
        skin_image = cv2.bitwise_and(self.original_image, self.original_image, mask = skin_mask)
        bs_mask = self.bsModel.apply(skin_image, learningRate = 0.01)
        self.solved_original_image = cv2.bitwise_and(skin_image, skin_image, mask = bs_mask)
        
    def thresholding(self):
        grey_image = cv2.cvtColor(self.solved_original_image, cv2.COLOR_BGR2GRAY)
        value = (35, 35)
        blurred = cv2.GaussianBlur(grey_image, value, 0)
        _, self.thresholded_image = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    def retrieveContours(self):
        self.contours, _ = cv2.findContours(self.thresholded_image.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    def retrieveHandContour(self):
        maxRegion, index = 0, 0
        for a in xrange(len(self.contours)):
            region = cv2.contourArea(self.contours[a])
            if region > maxRegion:
                maxRegion = region
                index = a
        self.single_hand_contour = self.contours[index]
        self.single_hand_length = cv2.arcLength(self.single_hand_contour, True)
        self.hand_contour = cv2.approxPolyDP(self.single_hand_contour, 0.001 * self.single_hand_length, True)

    def findHullDefects(self):
        self.hull = cv2.convexHull(self.hand_contour, returnPoints = False)
        self.hull_point = [self.hand_contour[a[0]] for a in self.hull]
        self.hull_point = np.array(self.hull_point, dtype = np.int32)
        self.defects = cv2.convexityDefects(self.hand_contour, self.hull)

    def findCenter(self):
        scale_percentage = 0.3
        s = np.array(self.hand_contour * scale_percentage, dtype=np.int32)
        temp_x, temp_y, j, k = cv2.boundingRect(s)
        max_point = None
        max_radius = 0
        for a in xrange(j):
            for b in xrange(k):
                r = cv2.pointPolygonTest(s, (temp_x + a, temp_y + b), True)
                if r > max_radius:
                    max_point = (temp_x + a, temp_y + b)
                    max_radius = r
        temp_center = np.array(np.array(max_point) / scale_percentage, dtype=np.int32)
        error = int((1 / scale_percentage) * 1.5)
        max_point = None
        max_radius = 0
        for a in xrange(temp_center[0] - error, temp_center[0] + error):
            for b in xrange(temp_center[1] - error, temp_center[1] + error):
                r = cv2.pointPolygonTest(self.hand_contour, (a, b), True)
                if r > max_radius:
                    max_point = (a, b)
                    max_radius = r
        return np.array(max_point)

    def findHandCenter(self):
        self.center = self.findCenter()
        self.radius = cv2.pointPolygonTest(self.hand_contour, tuple(self.center), True)
        self.hand_center += [tuple(self.center)]

    def findRealHandCenter(self):
        if len(self.hand_center) > 10:
            self.recent_position = sorted(self.hand_center[-30:])
            self.pos_x = [pos[0] for pos in self.recent_position]
            self.pos_y = [pos[1] for pos in self.recent_position]
        else:
            self.recent_position = []

    def originalRGBA(self, width_percentage=1, height_percentage=1):
        if width_percentage != 1 or height_percentage != 1:
            new_image = cv2.resize(self.original_image, (480, 320))
            return cv2.cvtColor(new_image, cv2.COLOR_BGR2RGBA)
        return cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGBA)    

    def thresholdingRGBA(self, width_percentage=1, height_percentage=1):
        if width_percentage != 1 or height_percentage != 1:
            new_image = cv2.resize(self.thresholded_image, (0, 0), fx=width_percentage, fy=height_percentage)
            return cv2.cvtColor(new_image, cv2.COLOR_GRAY2RGBA)
        return cv2.cvtColor(self.thresholded_image, cv2.COLOR_GRAY2RGBA)

    def canvasRGBA(self, width_percentage=1, height_percentage=1):
        if width_percentage != 1 or height_percentage != 1:
            new_image = cv2.resize(self.drawing_canvas, (0, 0), fx=width_percentage, fy=height_percentage)
            return cv2.cvtColor(new_image, cv2.COLOR_BGR2RGBA)
        return cv2.cvtColor(self.drawing_canvas, cv2.COLOR_BGR2RGBA)

    @staticmethod
    def BGRtoRGBA(image, width, height):
        new_image = cv2.resize(image, (width, height))
        return cv2.cvtColor(new_image, cv2.COLOR_BGR2RGBA)

    @staticmethod
    def GRAYtoRGBA(image, width, height):
        new_image = cv2.resize(image, (width, height))
        return cv2.cvtColor(new_image, cv2.COLOR_GRAY2RGBA)

    def paint(self):
        self.drawing_canvas = np.zeros(self.original_image.shape, np.uint8)
        if len(self.contours) != 0 :
            self.paintHand()
            self.paintHull()
            self.paintDefects()
            self.paintCenter()
            self.paintInscribedCircle()

    def paintCenter(self):
        cv2.circle(self.drawing_canvas, tuple(self.center), 10, (255, 0, 0), -2)
        if len(self.recent_position) != 0:
            for a in xrange(len(self.recent_position)):
                cv2.circle(self.drawing_canvas, self.recent_position[a], 5, (255, 25 * a, 25 * a), -1)

    def paintInscribedCircle(self):
        cv2.circle(self.drawing_canvas, tuple(self.center), int(self.radius), (0, 255, 0), 10)

    def paintHand(self):
        cv2.drawContours(self.drawing_canvas, [self.hand_contour], 0, (0, 255, 0), 1)

    def paintHull(self):
        cv2.drawContours(self.drawing_canvas, [self.hull_point], 0, (0, 0, 255), 2)

    def paintDefects(self):
        self.defect_point = []
        min_distance = 2000
        if self.defects != None:
            for a in self.defects:
                if a[0][3] > min_distance:
                    self.defect_point.append(self.hand_contour[a[0][2]])
            self.defect_point = np.array(self.defect_point, dtype=np.int32)
