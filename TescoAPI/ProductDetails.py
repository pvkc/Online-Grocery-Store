import httplib, urllib, base64

headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': '5f305236373e4b84bdd4754c5495a9e6',
}

params = urllib.urlencode({
    # Request parameters
    #'gtin': '{string}',
    'tpnb': '54550913',
    #'tpnc': '{string}',
})

try:
    conn = httplib.HTTPSConnection('dev.tescolabs.com')
    conn.request("GET", "/product/?%s" % params, "{body}", headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))

####################################


