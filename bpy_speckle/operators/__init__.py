from .accounts import LoadAccounts, AddAccount, LoadAccountStreams
from .object import UpdateObject, ResetObject, DeleteObject, UploadObject, UploadNgonsAsPolylines, SelectCustomProperty
from .streams import DownloadStreamObjects, UploadStreamObjects, ViewStreamDataApi, ViewStreamObjectsApi, DeleteStream, SelectOrphanObjects
from .streams import UpdateGlobal, CreateStream
from .cache import ClearObjectCache, ClearAccountCache, ClearStreamCache

operator_classes = [
	LoadAccounts, 
	AddAccount, 
	DownloadStreamObjects,
	UploadStreamObjects,
	ClearObjectCache, 
	ClearAccountCache, 
	ClearStreamCache, 
	LoadAccountStreams,
	]

operator_classes.extend([
	UpdateObject, 
	ResetObject, 
	DeleteObject, 
	UploadObject, 
	UploadNgonsAsPolylines,
	SelectCustomProperty,
	])

operator_classes.extend([
	ViewStreamDataApi, 
	ViewStreamObjectsApi, 
	DeleteStream, 
	SelectOrphanObjects,
	UpdateGlobal, 
	CreateStream,
	])