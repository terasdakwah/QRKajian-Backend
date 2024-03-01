from flask import Flask
from flask_mongoengine2 import MongoEngine
from pymongo import MongoClient
from flask_cors import CORS
from config import MONGODB_HOST, MONGODB_PORT, MONGODB_DB

app = Flask(__name__ , static_url_path='/static')
app.config.from_object('config')

CORS(app)

db = MongoEngine()
db.init_app(app)
mongo_client = MongoClient(MONGODB_HOST, MONGODB_PORT)
db_raw = mongo_client[MONGODB_DB]

# Import a module / component using its blueprint handler variable
from app.mod_apisv1.routes import mod_apisv1
from app.mod_user.controllers import mod_user
from app.mod_attendance.controllers import mod_attendance

# Register blueprint(s)
app.register_blueprint(mod_apisv1)
app.register_blueprint(mod_user)
app.register_blueprint(mod_attendance)