class AlphaBot(object):
	def __init__(self,in1=12,in2=13,ena=6,in3=20,in4=21,enb=26):
		self.IN1 = in1
		self.IN2 = in2
		self.IN3 = in3
		self.IN4 = in4
		self.ENA = ena
		self.ENB = enb

	def forward(self):
		print("forward")

	def stop(self):
		print("stop")

	def backward(self):
		print("backward")

	def left(self):
		print("left")

	def right(self):
		print("right")