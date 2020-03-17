'''
Speckle functions
'''

unit_scale = {
    'Meters':1.0,
    'Centimeters':0.01,
    'Millimeters':0.001,
    'Inches':0.0254,
    'Feet':0.3048,
    'Kilometers':1000.0,
}

'''
Utility functions
'''

def _report(msg):
    '''
    Function for printing messages to the console
    '''
    print("SpeckleBlender: {}".format(msg))

def get_scale_length(units):
    if units in unit_scale.keys():
        return unit_scale[units]
    return 1.0

def tuple_to_account(tup):
    assert len(tup) > 4

    profile = {}
    profile["server_name"] = tup[1]
    profile["server"] = tup[2]
    profile["email"] = tup[3]
    profile["apitoken"] = tup[4]

    return profile

'''
Client, account, and stream functions
'''

def _check_speckle_client_account_stream(scene):

        speckle = scene.speckle
        client = speckle.client
        account = None
        stream = None

        if client is None: 
            print ("SpeckleClient was not initialized...")

        if len(speckle.accounts) > 0 and speckle.active_account >= 0 and speckle.active_account < len(speckle.accounts):
            account = speckle.accounts[speckle.active_account]

        if account is None:
            print("No accounts loaded.")

        if len(account.streams) < 1:
            print("Account contains no streams.")

        if len(account.streams) > 0 and account.active_stream >= 0 and account.active_stream < len(account.streams):
            stream = account.streams[account.active_stream]

        if stream is None:
            print("Stream couldn't be loaded.")

        return (client, account, stream)

def _get_stream_objects(client, account, stream):

    client.server = account.server
    client.s.headers.update({'Authorization': account.authToken})

    if stream.query:
        _report(stream.query)
        res = client.StreamGetObjectsAsync(stream.streamId, stream.query)
    else:
        res = client.StreamGetObjectsAsync(stream.streamId)

    return res

def _add_account(client, cache, email, pwd, host, host_name="Speckle Hestia"):
    client.server = host

    if host is "":
        return False

    if not cache.try_connect():
        cache.create_database()

    if cache.account_exists(host, email):
        _report("Account already in database.")
        if True:
            cache.delete_account(host, email)
        else:
            return False

    try:
        client.login(email=email, password=pwd)
    except AssertionError as e:
        _report("Login failed.")
        return False

    #authtoken = client.get("me").get("apitoken")
    authtoken = client.me.get("apitoken")

    '''
    user = {
        'email': self.email, 
        'server': self.host,
        'server_name': "SpeckleServer",
        'apitoken': client.s.headers['Authorization']}
    '''
    cache.write_account(host, host_name, email, authtoken)

def _get_streams(client, account):

    client.server = account.server
    client.s.headers.update({
        'content-type': 'application/json',
        'Authorization': account.authToken,
    })



    res = client.StreamsGetAllAsync()
    if res == None or res['resources'] == None:
        return None

    account.streams.clear()

    streams = sorted(res['resources'], key=lambda x: x['name'], reverse=False)

    default_units = "Meters"

    for s in streams:
        stream = account.streams.add()
        stream.name = s['name']
        stream.streamId = s['streamId']
        bp = s.get("baseProperties")
        if bp:
            stream.units = bp.get("units", default_units)
        else:
            stream.units = default_units

def _get_accounts(scene):

    client = scene.speckle.client
    cache = scene.speckle.cache
    accounts = scene.speckle.accounts

    scene.speckle.accounts.clear()

    if not cache.try_connect():
        cache.create_database()

    profiles = cache.get_all_accounts()

    for profile in profiles:
        p = tuple_to_account(profile)

        account = accounts.add()
        account.name = p['server_name']
        account.server=p['server'] 
        account.email=p['email']
        account.authToken = p['apitoken']

def _create_stream(client, account, stream_name, units="Millimeters"):

    client.server = account.server
    client.s.headers.update({'Authorization': account.authToken})

    stream = {'name':stream_name, 'baseProperties':{'units':units}}

    client.streams.create(stream)

def _delete_stream(client, account, stream):
    client.server = account.server
    client.s.headers.update({'Authorization': account.authToken})

    if stream:
        res = client.streams.delete(stream.streamId)
        _report(res['message'])

'''
Cache functions
'''

def _clear_cache_objects(cache):
    if not cache.try_connect():
        return False

    cache.delete_all("CachedObject")
    return True

def _clear_cache_accounts(cache):
    if not cache.try_connect():
        return False

    cache.delete_all("Account")
    return True    

def _clear_cache_stream(cache):
    if not cache.try_connect():
        return False

    cache.delete_all("CachedStream")
    return True    