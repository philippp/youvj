class VidFail(Exception):
    msg = "An error occured"
    rc = -1
    def __init__(self, msg=None):
        if msg != None:
            self.msg = msg
            Exception.__init__(self, self.msg)

class InvalidEmail(VidFail):
    rc = 1000
    msg = "If you're new, click sign up!"

class InvalidPassword(VidFail):
    rc = 1001
    msg = "Wrong Password"

class WeakPassword(VidFail):
    rc = 1001
    msg = "Pick a better password :)"

class UserExists(VidFail):
    rc = 1002
    msg = "User already exists"

class InvalidSessionSignature(VidFail):
    rc = 1003
    msg = "Invalid Session Signature"
