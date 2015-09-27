tasks = []

class Task:
	def __init__(self, text, cssClass="info"):
		self.text = text
		self.cssClass = cssClass
		tasks.append(self)
