import base64, hmac
import hashlib
import random
import time
import operator

import config

BASE64_BLOCK_SIZE = 8
BASE64_PADDING_CHARACTER = '='

def trimBase64(b64):
    b64 = b64.replace('\n', '')
    b64 = b64.replace('=', '')
    b64 = b64.replace('+', '_')
    b64 = b64.replace('/', '-')
    return b64

# add back the '=' padding and fix remap url-safe tokens                                                                                                                                                                                   
def fattenBase64(buffer):
    buffer = buffer.replace('_', '+')
    buffer = buffer.replace('-', '/')
    
    padding = BASE64_PADDING_CHARACTER * (BASE64_BLOCK_SIZE - (len(buffer) % BASE64_BLOCK_SIZE))
    return buffer + padding


def sign_dict(to_sign):
    to_sign_pairs = sorted(to_sign.items(), key = operator.itemgetter(0))
    to_sign_str = "&".join(map(lambda p : "%s=%s" % (p[0], p[1]), to_sign_pairs))
    my_digest = hashlib.sha1(to_sign_str+config.session_secret).hexdigest()
    signature = trimBase64(base64.encodestring(my_digest))
    return signature

def generate_secret(length=32):
    random.seed()
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+'
    return reduce(lambda x,y: x+y, random.sample(alphabet, length))

def hash_pass(raw_password, salt):
    return hashlib.sha1("%s-%s" % (raw_password, salt)).hexdigest()

def auth_user( user_data, raw_password ):
    db_hash = user_data['passwd_hash']
    my_hash = hash_pass( raw_password, user_data['salt'] )
    return db_hash == my_hash

def encode_session( user_data ):
    session_dict = {
        'id':user_data['id'],
        'timestamp':time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    session_dict['signature'] = sign_dict( session_dict )
    pairs = sorted(session_dict.items(), key = operator.itemgetter(0))
    session_str = "&".join(map(lambda p : "%s=%s" % (p[0], p[1]), pairs))
    return trimBase64(base64.b64encode( session_str ))

def decode_session( session_str ):
    session_str = base64.b64decode( fattenBase64(session_str) )
    session_dict = dict( [p.split("=") for p in session_str.split("&")] )
    signature = session_dict['signature']
    del session_dict['signature']
    if signature == sign_dict( session_dict ):
        return session_dict
    else:
        raise vidfail.InvalidSessionSignature()
