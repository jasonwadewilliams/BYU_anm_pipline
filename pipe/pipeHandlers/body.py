import os

from pipe.pipeHandlers.element import Element
from pipe.pipeHandlers.environment import Environment
from pipe.pipeHandlers import pipeline_io

'''
body module
'''

class Body(object):
	'''
	Abstract class describing bodies that make up a project.
	'''
	PIPELINE_FILENAME = '.body'

	NAME = 'name'
	REFERENCES = 'references'
	DESCRIPTION = 'description'
	TYPE = 'type'
	FRAME_RANGE = 'frame_range'
	CAMERA_NUMBER = 'camera_number'

	@staticmethod
	def create_new_dict(name):
		'''
		populate a dictionary with all the fields needed to create a new body
		'''
		datadict = {}
		datadict[Body.NAME] = name
		datadict[Body.REFERENCES] = []
		datadict[Body.DESCRIPTION] = ''
		datadict[Body.TYPE] = AssetType.ASSET
		datadict[Body.FRAME_RANGE] = 0
		return datadict

	@staticmethod
	def get_parent_dir():
		'''
		return the parent directory that bodies of this type are stored in
		'''
		return Environment().get_assets_dir()

	def __init__(self, filepath):
		'''
		creates a Body instance describing the asset or shot stored in the given filepath
		'''
		self._env = Environment()
		self._filepath = filepath
		self._pipeline_file = os.path.join(filepath, Body.PIPELINE_FILENAME)
		if not os.path.exists(self._pipeline_file):
			raise EnvironmentError('not a valid body: ' + self._pipeline_file + ' does not exist')
		self._datadict = pipeline_io.readfile(self._pipeline_file)

	def __str__(self):
		name = self.get_name()
		filepath = self.get_filepath()
		type = self.get_type()

		return "<Body Object of TYPE " + str(type) + " with NAME " + str(name) + " AT " + str(filepath) + ">"

	def get_name(self):

		return self._datadict[Body.NAME]

	def get_filepath(self):
		return self._filepath

	def is_shot(self):
		if self.get_type() == AssetType.SHOT:
			return True
		else:
			return False

	def is_set(self):
		if self.get_type() == AssetType.SET:
			return True
		else:
			return False

	def is_asset(self):
		return True

	def is_tool(self):

		raise NotImplementedError('subclass must implement is_tool')

	def is_crowd_cycle(self):

		raise NotImplementedError('subclass must implement is_crowd_cycle')

	def get_description(self):

		return self._datadict[Body.DESCRIPTION]

	def get_type(self):

		return self._datadict[Body.TYPE]

	def update_type(self, new_type):

		self._datadict[Body.TYPE] = new_type
		pipeline_io.writefile(self._pipeline_file, self._datadict)

	def get_frame_range(self):

		return self._datadict[Body.FRAME_RANGE]

	def set_frame_range(self, frame_range):
		self._datadict[Body.FRAME_RANGE] = frame_range
		pipeline_io.writefile(self._pipeline_file, self._datadict)

	def update_frame_range(self, frame_range):

		self._datadict[Body.FRAME_RANGE] = frame_range
		pipeline_io.writefile(self._pipeline_file, self._datadict)

	def get_camera_number(self):
		return self._datadict[Body.CAMERA_NUMBER]

	def set_camera_number(self, num):
		self._datadict[Body.CAMERA_NUMBER] = num
		pipeline_io.writefile(self._pipeline_file, self._datadict)

	def version_prop_json(self, prop, filepath):
		files = os.listdir(filepath)

		latest_version = -1
		for file in files:
			filename, ext = os.path.splitext(file)

			if not str(ext) == ".json":
				continue
			if str(prop) not in str(filename):
				continue

			name_and_version = str(filename).split("_")
			version = name_and_version[-1]

			if int(version) > latest_version:
				latest_version = int(version)

		latest_version += 1

		return latest_version, str(latest_version)

	def get_element(self, department, name=Element.DEFAULT_NAME, force_create=False):
		'''
		get the element object for this body from the given department. Raises EnvironmentError
		if no such element exists.
		department -- the department to get the element from
		name -- the name of the element to get. Defaults to the name of the
				element created by default for each department.
		'''
		print('looking for element', name)

		element_dir = os.path.join(self._filepath, department)
		if not os.path.exists(element_dir):
			if force_create:
				try:
					self.create_element(department, name)
				except Exception as e:
					print(e)
			else:
				raise EnvironmentError('no such element: ' + element_dir + ' does not exist')

		return Element(element_dir)

	def create_element(self, department, name):
		'''
		create an element for this body from the given department and return the
		resulting element object. Raises EnvironmentError if the element already exists.
		department -- the department to create the element for
		name -- the name of the element to create
		'''
		dept_dir = os.path.join(self._filepath, department)
		if not os.path.exists(dept_dir):
			pipeline_io.mkdir(dept_dir)
		
		empty_element = Element()
		datadict = empty_element.create_new_dict(name, department, self.get_name())
		if os.path.exists(os.path.join(dept_dir, empty_element.PIPELINE_FILENAME)):
			print("element already exists: " + dept_dir)
			return None

		pipeline_io.writefile(os.path.join(dept_dir, empty_element.PIPELINE_FILENAME), datadict)
		return self.set_app_ext(department, dept_dir)

	def set_app_ext(self, department, filepath=None):
		'''
		this function sets the file extension for an element.
		'''
		element = Element(filepath)

		if department == Asset.GEO:
			element.update_app_ext(".obj")
			return element
		elif department == Asset.ANIMATION or department == Asset.CAMERA:
			element.update_app_ext(".abc")
			return element
		elif department == Asset.RIG:
			element.update_app_ext(".mb")
			return element
		else:
			return element

	def list_elements(self, department):
		'''
		return a list of all elements for the given department in this body
		'''
		subdir = os.path.join(self._filepath, department)
		if not os.path.exists(subdir):
			return []
		dirlist = os.listdir(subdir)
		elementlist = []
		for elementdir in dirlist:
			abspath = os.path.join(subdir, elementdir)
			if os.path.exists(os.path.join(abspath, Element.PIPELINE_FILENAME)):
				elementlist.append(elementdir)
		elementlist.sort()
		return elementlist

	def add_reference(self, reference):
		'''
		Add the given reference to this body. If it already exists, do nothing. If reference is not a valid
		body, raise an EnvironmentError.
		'''
		ref_asset_path = os.path.join(self._env.get_assets_dir(), reference, Body.PIPELINE_FILENAME)
		ref_shot_path = os.path.join(self._env.get_shots_dir(), reference, Body.PIPELINE_FILENAME)
		ref_crowd_path = os.path.join(self._env.get_crowds_dir(), reference, Body.PIPELINE_FILENAME)
		if not os.path.exists(ref_asset_path) and not os.path.exists(ref_shot_path) and not os.path.exists(ref_crowd_path):
			raise EnvironmentError(reference + ' is not a valid body')
		if reference not in self._datadict[Body.REFERENCES]:
			self._datadict[Body.REFERENCES].append(reference)
		pipeline_io.writefile(self._pipeline_file, self._datadict)

	def remove_reference(self, reference):
		'''
		Remove the given reference, if it exists, and return True. Otherwise do nothing, and return False.
		'''
		try:
			self._datadict[Body.REFERENCES].remove(reference)
			return True
		except ValueError:
			return False
		pipeline_io.writefile(self._pipeline_file, self._datadict)

	def update_description(self, description):

		self._datadict[Body.DESCRIPTION] = description
		pipeline_io.writefile(self._pipeline_file, self._datadict)

	def get_references(self):
		'''
		Return a list of all references for this body.
		'''
		return self._datadict[Body.REFERENCES]

	def has_relation(self, attribute, relate, value):
		'''
		Return True if this body has the given attribute and if the given relationship
		to the the given value. Return False otherwise
		'''
		if attribute not in self._datadict:
			return False
		return relate(self._datadict[attribute],value)

class AssetType:
	'''
	Class describing types of assets.
	'''

	TOOL = 'tool'
	SHOT = 'shot'
	ASSET = 'asset'
	SET = 'set'
	SEQUENCE = 'sequence'
	ALL = [ASSET, SHOT, TOOL, SET, SEQUENCE]
	MAYA = [ASSET, SHOT, SET]

	def __init__(self):
		pass

	def list_asset_types(self):
		return self.ALL

	def list_maya_types(self):
		return self.MAYA

class Asset(Body):
	'''
	Class describing an asset body.
	'''
	GEO = 'geo'
	CAMERA = 'camera'
	ANIMATION = 'animation'
	RIG = 'rig'
	HDA = 'hda'
	TEXTURES = 'textures'
	MATERIALS = 'materials'
	LIGHTS = 'lights'
	HIP = 'hip'
	LAYOUT = 'layout'
	USD = 'usd'
	MAYA = 'maya'
	'''
	These are the "departments" refered to in the Element class. The current pipeline creates
	all of these departments for every type of Body object.
	'''
	ALL = [GEO, CAMERA, ANIMATION, RIG, HDA, TEXTURES, MATERIALS, LIGHTS, HIP, LAYOUT, USD, MAYA]

	@staticmethod
	def create_new_dict(name):
		datadict = Body.create_new_dict(name)
		return datadict

	def __str__(self):
		return super(Asset, self).__str__()

	def is_tool(self):
		return False

	def is_crowd_cycle(self):
		return False


class Shot(Body):
	'''
	Class describing a shot body.
	'''

	@staticmethod
	def create_new_dict(name):
		datadict = {}
		datadict[Body.NAME] = name
		datadict[Body.REFERENCES] = []
		datadict[Body.DESCRIPTION] = ''
		datadict[Body.TYPE] = AssetType.SHOT
		datadict[Body.FRAME_RANGE] = 0
		return datadict

	@staticmethod
	def get_parent_dir():
		return Environment().get_shots_dir()

	def __str__(self):
		return super(Shot, self).__str__()

	def is_tool(self):
		return False

	def is_crowd_cycle(self):
		return False

class Sequence(Body):
	'''
	Class describing a sequence body.
	'''

	@staticmethod
	def create_new_dict(name):
		datadict = {}
		datadict[Body.NAME] = name
		datadict[Body.TYPE] = AssetType.SEQUENCE
		return datadict

	@staticmethod
	def get_parent_dir():
		return Environment().get_sequences_dir()

	def is_tool(self):
		return False

	def is_crowd_cycle(self):
		return False

class Layout(Body):
	'''
	Class describing a layout body.
	'''

	@staticmethod
	def create_new_dict(name):
		datadict = {}
		datadict[Body.NAME] = name
		datadict[Body.REFERENCES] = []
		datadict[Body.DESCRIPTION] = ''
		datadict[Body.TYPE] = AssetType.SET
		datadict[Body.FRAME_RANGE] = 0
		return datadict

	@staticmethod
	def get_parent_dir():
		return Environment().get_layouts_dir()

	def __str__(self):
		return super(Layout, self).__str__()

	def is_tool(self):
		return False

	def is_crowd_cycle(self):
		return False


class Tool(Body):
	'''
	Class describing a tool body.
	'''

	@staticmethod
	def create_new_dict(name):

		datadict = Body.create_new_dict(name)
		return datadict

	@staticmethod
	def get_parent_dir():
		return Environment().get_tools_dir()

	def __str__(self):
		return super(Tool, self).__str__()

	def is_shot(self):

		return False

	def is_asset(self):

		return False

	def is_tool(self):

		return True

	def is_crowd_cycle(self):

		return False

class CrowdCycle(Body):
	'''
	Class describing a crowd cycle body.
	'''

	@staticmethod
	def create_new_dict(name):

		datadict = Body.create_new_dict(name)
		return datadict

	def __str__(self):
		return super(CrowdCycle, self).__str__()

	def is_shot(self):

		return False

	def is_asset(self):

		return False

	def is_tool(self):

		return False

	def is_crowd_cycle(self):

		return True
