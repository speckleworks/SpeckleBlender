from .accounts import SpeckleLoadAccounts, SpeckleAddAccount, SpeckleImportStream2,SpeckleClearObjectCache, SpeckleClearAccountCache, SpeckleClearStreamCache, SpeckleLoadAccountStreams
from .object import SpeckleUpdateObject, SpeckleResetObject, SpeckleDeleteObject, SpeckleUploadObject, SpeckleUploadNgonsAsPolylines
from .streams import SpeckleViewStreamDataApi, SpeckleViewStreamObjectsApi, SpeckleDeleteStream, SpeckleSelectOrphanObjects
from .streams import SpeckleUpdateGlobal, SpeckleUploadStream, SpeckleCreateStream

operator_classes = [
	SpeckleLoadAccounts, 
	SpeckleAddAccount, 
	SpeckleImportStream2,
	SpeckleClearObjectCache, 
	SpeckleClearAccountCache, 
	SpeckleClearStreamCache, 
	SpeckleLoadAccountStreams,
	]

operator_classes.extend([
	SpeckleUpdateObject, 
	SpeckleResetObject, 
	SpeckleDeleteObject, 
	SpeckleUploadObject, 
	SpeckleUploadNgonsAsPolylines,
	])

operator_classes.extend([
	SpeckleViewStreamDataApi, 
	SpeckleViewStreamObjectsApi, 
	SpeckleDeleteStream, 
	SpeckleSelectOrphanObjects,
	SpeckleUpdateGlobal, 
	SpeckleUploadStream, 
	SpeckleCreateStream,
	])