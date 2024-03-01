from flask import Blueprint
from flask_restful import Api, Resource, url_for
from app.mod_apisv1.resources.attendance import FillAttendanceRes
from app.mod_apisv1.resources.user import UserDataRes, UserSedekahRes

mod_apisv1 = Blueprint('mod_apisv1', __name__, url_prefix='/apis/v1')
apis = Api(mod_apisv1)

apis.add_resource(FillAttendanceRes, '/attendance/fill')
apis.add_resource(UserDataRes, '/user/data')
apis.add_resource(UserSedekahRes, '/user/sedekah')
