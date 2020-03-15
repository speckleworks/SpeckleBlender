from .scene import SpeckleSceneSettings, SpeckleSceneObject, SpeckleUserAccountObject, SpeckleStreamObject
from .object import SpeckleObjectSettings
from .collection import SpeckleCollectionSettings
from .addon import SpeckleAddonPreferences

property_classes = [
	SpeckleSceneObject, 
	SpeckleStreamObject,
	SpeckleUserAccountObject, 
	SpeckleSceneSettings, 
	SpeckleObjectSettings,
	SpeckleCollectionSettings,
	SpeckleAddonPreferences,
	]