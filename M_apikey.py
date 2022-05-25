import os

# OWM Key Github Actions Repo Secret
def getkey():
    key = os.environ['OWM_APIKEY']
    return (key)