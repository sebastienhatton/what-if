# Utility function for connecting to the Mongo database
import mongoengine
def connect_mongo():
    mongoengine.connect('whatif')
connect_mongo()

# Some project specific properties
import os
PROJECT_PATH = os.path.dirname(globals()["__file__"])
SECRET_KEY = 'y!j#d42iji*v(y!%$b4gm0g@!d423-^%@=hf2nt29rb6!us&cp'