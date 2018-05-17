import json

class SpeckleStream(object):
	streamId = ""
	name = ""
	objects = []
	layers = []
	baseProperties = None
	globalMeasures = None
	isComputedResult = False
	viewerLayers = []
	parent = ""
	children = []
	ancestors = []

	def __init__(self, j = None):
		if j is not None:
			self.from_json(j)
		else:
			self.name = "SpeckleStream"

	def to_json(self):
		layers = [x.__dict__ for x in self.layers]
		self.layers = layers
		objects = [x.__dict__ for x in self.objects]
		self.objects = objects
		return json.dumps(self.__dict__, sort_keys = True)

	def from_json(self, j):
		if type(j) is dict:
			self.__dict__ = j
		else:
			self.__dict__ = json.loads(j)
