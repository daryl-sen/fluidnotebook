import base64

def url_encode(num):
        bts = base64.b64encode(bytes(str(num), 'utf-8'))
        return bts.decode()

def url_decode(bytes):
    return int(base64.b64decode(bytes))
