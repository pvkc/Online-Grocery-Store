import httplib, urllib, base64

headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': '5f305236373e4b84bdd4754c5495a9e6',
}

params = urllib.urlencode({
})

try:
    conn = httplib.HTTPSConnection('dev.tescolabs.com')
    conn.request("GET", "/grocery/products/?query=milk&offset=0&limit=10&%s" % params, "{body}", headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    print(conn.url)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))

####################################

