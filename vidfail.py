class VidFail(Exception):
    msg = "An error occured"
    rc = -1
    def __init__(self, msg=None):
        if msg != None:
            self.msg = msg
            Exception.__init__(self, self.msg)

class InvalidPassword(VidFail):
    rc = 1000
    msg = "Invalid email or password"

class UserExists(VidFail):
    rc = 1001
    msg = "User already exists"

class InvalidSessionSignature(VidFail):
    rc = 1002
    msg = "Invalid Session Signature"
