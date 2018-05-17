import json

class SpeckleResource(object):
	_id = ""
	owner = ""
	private = False
	anonymousComments = True
	canRead = True
	canWrite = True
	comments = []
	deleted = False

	def __init__(self, j = None):
		if j is not None:
			self.from_json(j)

	def to_json(self):
		return json.dumps(self.__dict__, sort_keys = True)

	def from_json(self, j):
		if type(j) is dict:
			self.__dict__ = j
		else:
			self.__dict__ = json.loads(j)
