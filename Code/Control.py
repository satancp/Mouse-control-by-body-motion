import pyautogui
import math

class Control(object):

	def __init__(self):
		self.times = 0
		self.screenWidth, self.screenHeight = pyautogui.size()
		self.currentMouseX, self.currentMouseY = pyautogui.position()
		pyautogui.FAILSAFE = False
		self.signal = False
		self.finger_number_previous = 0

	def getCursorPosition(self):
		self.currentMouseX, self.currentMouseY = pyautogui.position()

	def moveCursor(self, distanceX, distanceY, speed):
		self.getCursorPosition()
		duration = 10 / speed
		estimatedX = distanceX + self.currentMouseX
		estimatedY = distanceY + self.currentMouseY
		moveX, moveY = distanceX, distanceY
		if estimatedX >= self.screenWidth :
			moveX = self.screenWidth - self.currentMouseX
		elif estimatedX < 0 :
			moveX = 0 - self.currentMouseX
		if estimatedY >= self.screenHeight :
			moveY = self.screenHeight - self.currentMouseY
		elif estimatedY < 0 :
			moveY = 0 - self.currentMouseY
		pyautogui.moveRel(moveX, moveY, duration = duration)

	def clickMouse(self, buttonName, number):
		pyautogui.click(button = buttonName, clicks = number)

	def dragCursor(self, buttonName, distanceX, distanceY, speed):
		pyautogui.mouseDown(button = buttonName)
		self.moveCursor(distanceX, distanceY, speed)
		pyautogui.mouseUp(button = buttonName)

	def scroll(self, distanceX, distanceY):
		if self.abs_dX <= self.abs_dY :
			pyautogui.scroll(distanceY)
		else :
			pyautogui.hscroll(distanceX)

	def setDefaultData(self, original_center):
		self.last_center = original_center
		self.current_center = original_center

	def reflectControll(self, index):
		return {
		'1':self.moveCursor(self.distanceX, self.distanceY, self.speed),
		'2':self.scroll(self.distanceX, self.distanceY)
		'4':self.clickMouse('left',1)
		}.get(index,self.moveCursor(self.distanceX, self.distanceY, self.speed))

	def distanceAnalysis(self, current_center):
		self.last_center = self.current_center
		self.current_center = current_center
		self.distanceX = (self.current_center[0] - self.last_center[0]) * 1.5
		self.distanceY = (self.current_center[1] - self.last_center[1]) * 1.5
		self.abs_dX = math.pow(self.distanceX, 2)
		self.abs_dY = math.pow(self.distanceY, 2)
		self.movement_distance = math.pow(self.abs_dX + self.abs_dY, 0.5)
		self.speed = self.movement_distance / 0.1
		if self.movement_distance > 200 :
			pyautogui.FAILSAFE = True
		else :
			pyautogui.FAILSAFE = False

	def gestureAnalysis(self, defect_points, current_center):
		if self.times == 0 :
			self.setDefaultData(current_center)
			self.times = 1
		else :
			self.distanceAnalysis(current_center)
			self.finger_number = len(defect_points) - 2
			if self.finger_number == 5 :
				if self.signal == False:
					self.signal = True
			if self.finger_number < 1 or self.finger_number > 5 :
				if self.signal == True :
					self.signal = False
			if self.signal == True and self.speed != 0 :
				if self.finger_number_previous == 1 and self.finger_number == 0 :
					self.clickMouse('left', 1)
				else :
					self.reflectControll(self.finger_number)