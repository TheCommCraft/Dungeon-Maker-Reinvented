from os import getenv, system
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..")))
try:
    from dungeonmaker.dm_backend import DMBackend
    from dungeonmaker.dm_backend.modules.database import MongoDBAtlasSession
    from dotenv import load_dotenv
    import scratchcommunication, time, sys
except ModuleNotFoundError:
    system("pip install --upgrade -r requirements.txt")
    from dungeonmaker.dm_backend import DMBackend
    from dungeonmaker.dm_backend.modules.database import MongoDBAtlasSession
    from dotenv import load_dotenv
    import scratchcommunication, time

load_dotenv()

SCRATCH_USERNAME = getenv("SCRATCH_USERNAME")
SCRATCH_SESSIONID = getenv("SCRATCH_SESSIONID")
SCRATCH_PASSWORD = getenv("SCRATCH_PASSWORD")
SCRATCH_XTOKEN = getenv("SCRATCH_XTOKEN")
SCRATCH_PROJECT_ID = getenv("SCRATCH_PROJECT_ID")
SCRATCH_SECURITY_KEY = getenv("SCRATCH_SECURITY_KEY")
MONGO_DB_ATLAS_URI = getenv("MONGO_DB_ATLAS_URI")

if SCRATCH_SESSIONID:
    session = scratchcommunication.Session(username=SCRATCH_USERNAME, session_id=SCRATCH_SESSIONID, xtoken=SCRATCH_XTOKEN)
else:
    session = scratchcommunication.Session.login(username=SCRATCH_USERNAME, password=SCRATCH_PASSWORD)
print(session.username)
cloud = scratchcommunication.Sky(session.create_cloudconnection(SCRATCH_PROJECT_ID), session.create_tw_cloudconnection(SCRATCH_PROJECT_ID, contact_info="TheCommCraft on scratch"))
mongo_db = MongoDBAtlasSession(URI=MONGO_DB_ATLAS_URI)
security = scratchcommunication.security.Security.from_string(SCRATCH_SECURITY_KEY)
print(security.public_data)
dm_backend = DMBackend(cloud=cloud, project_id=SCRATCH_PROJECT_ID, db_session=mongo_db, security=security)
print(time.time())
dm_backend.run(duration=600, thread=False)
dm_backend.stop()
print(time.time())
sys.exit()