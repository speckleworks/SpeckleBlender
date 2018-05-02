import requests, json, os
import struct, base64

from .util import SPrint

class SpeckleClient(object):
    def __init__(self):
        self.baseUrl = "https://hestia.speckle.works/api/v1"
        self.authToken = ""
        self.useGzip = True

    '''
    Utility functions
    '''
    def check_response_status_code(self, r):
        # parse response
        if r.status_code == 200:
            SPrint("Request successful: %s" % r.reason)
            return True
        elif r.status_code == 400:
            SPrint("Request failed: %s" % r.reason)
            #print(r.text)
        elif r.status_code != 200 and r.status_code != 204:
            SPrint("The HTTP status code of the response was not expected: %s, %s" % (r.status_code, r.reason))

        return False

    def PrepareResponse(self, header):
        if self.authToken:
            header['Authorization'] = self.authToken

    def LoadProfiles(self):
        profiles = {}
        path = os.path.join(os.getenv('LOCALAPPDATA'), 'SpeckleSettings')
        if os.path.isdir(path):
            files = [os.path.join(path, x) for x in os.listdir(path) if x.endswith('.txt')]
            for file in files:
                with open(file, 'r') as f:
                    line = f.readline()
                    tokens = line.split(',')
                    profiles[tokens[0]] = {'name': tokens[2], 'authtoken': tokens[1], 'server': tokens[3]}

        return profiles

    def SaveNewProfile(self, profile):
        assert ("email" in profile.keys())
        assert ("server_name" in profile.keys())
        assert ("authtoken" in profile.keys())

        path = os.path.join(os.getenv('LOCALAPPDATA'), 'SpeckleSettings')
        if os.path.isdir(path):
            with open(os.path.join(path, profile['email']) + ".JWT .txt", 'w') as f:
                f.writeline("%s,%s,%s,%s,%s" % (profile['email'], profile['authtoken'], profile['server_name'], profile['server'], profile['server']))

    def UseExistingProfile(self, email):
        profiles = self.LoadProfiles()
        if email in profiles.keys():
            self.baseUrl = profiles[email]['server']
            self.authToken = profiles[email]['authtoken']
            return True
        return False

    '''
    Client methods
    '''
    def UserRegister(self, profile):
        assert ("server_name" in profile.keys())
        assert ("email" in profile.keys())
        assert ("password" in profile.keys())
        assert ("name" in profile.keys())
        assert ("surname" in profile.keys())

        url = self.baseUrl + "/accounts/register"

        headers = {'content-type' : 'application/json'}
        r = requests.post(url, data=json.dumps(profile), headers=headers)

        if self.check_response_status_code(r):
            

            return r.json()
        return None

    def UserLogin(self, login_dict):
        assert ("email" in login_dict.keys())
        assert ("password" in login_dict.keys())

        url = self.baseUrl + "/accounts/login"

        headers = {'content-type' : 'application/json'}
        r = requests.post(url, data=json.dumps(login_dict), headers=headers)

        if self.check_response_status_code(r):
            login_response = r.json()
            #print(login_response['resource'].keys())
            self.authToken = login_response['resource']['apitoken']
            return login_response
        return None

    def GetStreams(self):
        url = self.baseUrl + "/streams"

        headers = {'content-type' : 'application/json'}
        self.PrepareResponse(headers)
        r = requests.get(url, headers=headers)

        if self.check_response_status_code(r):
            return r.json()
        return None

    def UserClientsGet(self):
        url = self.baseUrl + "/accounts/clients"

        headers = {'content-type' : 'application/json'}

        self.PrepareResponse(headers)
        r = requests.get(url, headers=headers)

        if self.check_response_status_code(r):
            return r.json()
        return None

    def UserGetProfile(self):
        url = self.baseUrl + "/accounts/profile"

        headers = {'content-type' : 'application/json'}
        
        self.PrepareResponse(headers)
        r = requests.get(url, headers=headers)

        if self.check_response_status_code(r):
            return r.json()
        return None     

    def UserUpdateProfile(self, update_dict):
        assert ("email" in update_dict.keys())
        assert ("name" in update_dict.keys())
        assert ("surname" in update_dict.keys())
        assert ("company" in update_dict.keys())

        url = self.baseUrl + "/accounts/profile"

        headers = {'content-type' : 'application/json'}
        
        self.PrepareResponse(headers)
        r = requests.put(url, data=json.dumps(login_dict), headers=headers)

        if self.check_response_status_code(r):
            return r.json()
        return None         

    def ClientCreate(self, create_dict):
        assert ("client" in create_dict.keys())

        url = self.baseUrl + "/clients"

        headers = {'content-type' : 'application/json'}

        self.PrepareResponse(headers)
        r = requests.post(url, data=json.dumps(create_dict), headers=headers)

        if self.check_response_status_code(r):
            return r.json()
        return None 

    def ClientGet(self, clientId):
        if not clientId: raise

        url = self.baseUrl + "/clients/%s" % clientId

        headers = {'content-type' : 'application/json'}

        self.PrepareResponse(headers)
        r = requests.get(url, headers=headers)

        if self.check_response_status_code(r):
            return r.json()
        return None 

    def ClientUpdate(self, update_dict, clientId):
        assert ("client" in update_dict.keys())

        if not clientId: raise

        url = self.baseUrl + "/clients/%s" % clientId

        headers = {'content-type' : 'application/json'}

        self.PrepareResponse(headers)
        r = requests.put(url, data=json.dumps(update_dict), headers=headers)

        if self.check_response_status_code(r):
            return r.json()
        return None         

    def ClientDelete(self, clientId):
        if not clientId: raise

        url = self.baseUrl + "/clients/%s" % clientId

        headers = {'content-type' : 'application/json'}

        self.PrepareResponse(headers)
        r = requests.delete(url, headers=headers)

        if self.check_response_status_code(r):
            return r.json()
        return None 

    def StreamCreate(self, name="Speckle Stream", layers=None):
        create_dict = {"name" : name}
        if layers is None:
            create_dict['layers'] = ""
        else:
            create_dict['layers'] = layers

        assert ("layers" in create_dict.keys())
        assert ("name" in create_dict.keys())

        url = self.baseUrl + "/streams"

        headers = {'content-type' : 'application/json'}

        self.PrepareResponse(headers)
        r = requests.post(url, data=json.dumps(create_dict), headers=headers)

        if self.check_response_status_code(r):
            return r.json()
        return None 

    def StreamDelete(self, streamId):

        url = self.baseUrl + "/streams/%s" % streamId
        headers = {'content-type' : 'application/json'}

        self.PrepareResponse(headers)
        r = requests.delete(url, headers=headers)

        if self.check_response_status_code(r):
            return r.json()
        return None 

    def GetStreamObjects(self, query, streamId):
        assert streamId is not None
        url = self.baseUrl + "/streams/%s/" % streamId
        if query is not None:
            url = url + "?" + query

        headers = {'content-type' : 'application/json'}

        self.PrepareResponse(headers)
        r = requests.get(url, headers=headers)

        if self.check_response_status_code(r):
            return r.json()
        return None 

    def ObjectCreate(self, obj):
        url = self.baseUrl + "/objects"

        if isinstance(obj, dict):
            payload = obj
        else:
            payload = obj.__dict__

        if '_id' in payload.keys():
            del payload['_id']

        headers = {'content-type' : 'application/json'}

        self.PrepareResponse(headers)
        r = requests.post(url, json.dumps(payload), headers=headers)

        if self.check_response_status_code(r):
            return r.json()
        return None 

    def ObjectToStream(self, objectId, streamId):
        assert objectId is not None
        assert streamId is not None

        url = self.baseUrl + "/streams/%s" % streamId
        headers = {'content-type' : 'application/json'}

        res = GetStreamObjects(self, None, streamId)
        print (res)

        self.PrepareResponse(headers)
        r = requests.put(url, json.dumps({"objects":[objectId]}), headers=headers)

        if self.check_response_status_code(r):
            return r.json()
        return None 

    def AddObjects(self, obj, streamId):
        assert streamId is not None
        if len(obj) == -1:
            payload = {"object":obj[0]} if isinstance(obj[0], dict) else {"object":obj[0].__dict__}
        else:
            payload = {"objects":[x if isinstance(x, dict) or isinstance(x, str) else x.__dict__ for x in obj ]}
        #payload = {"objects":[obj]}
        #SPrint (json.dumps(payload, indent=4, sort_keys=True))

        url = self.baseUrl + "/streams/%s" % streamId
        headers = {'content-type' : 'application/json'}

        self.PrepareResponse(headers)
        #SPrint(url)
        r = requests.put(url, json.dumps(payload), headers=headers)
        #print(r.text)

        if self.check_response_status_code(r):
            return r.json()
        return None

    def UpdateObject(self, obj):
        assert obj._id is not None

        url = self.baseUrl + "/objects/%s" % obj._id

        if isinstance(obj, dict):
            payload = obj
        else:
            payload = obj.__dict__

        headers = {'content-type' : 'application/json'}
        self.PrepareResponse(headers)
        r = requests.put(url, json.dumps(payload), headers=headers)

        if self.check_response_status_code(r):
            return r.json()
        return None

    def GetObject(self, objectId):
        assert objectId is not None
        url = self.baseUrl + "/objects/%s" % objectId
        headers = {'content-type' : 'application/json'}

        self.PrepareResponse(headers)
        r = requests.get(url, headers=headers)

        if self.check_response_status_code(r):
            return r.json()
        return None

if __name__ == '__main__':
    s = SpeckleClient()
    profiles = s.LoadProfiles()
    print (json.dumps(profiles, indent=4, sort_keys=True))
    s.UseExistingProfile(profiles[0])

    res = s.GetStreams()

    if res is not None:
        for i in res['resources']:
            SPrint(i['streamId'])
            objects = s.GetStreamObjects(None, i['streamId'])
            print (json.dumps(objects, indent=4, sort_keys=True))
            print()



