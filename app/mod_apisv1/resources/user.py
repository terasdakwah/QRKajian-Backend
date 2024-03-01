from datetime import datetime, timedelta
import traceback 
from flask_restful import Resource, url_for, request
from app.mod_apisv1.common.utils import string_datetime, return_error
from app.mod_user.models import User
from mongoengine.queryset.visitor import Q

class UserDataRes(Resource):
    def post(self):
        try:
            waktu = datetime.now()
            data_rq = request.get_json(force=True)
            token_id = data_rq['token_id']

            if not token_id:
                return return_error(402, 'Gagal')

            user = User.objects(id=token_id).first()
            if not user:
                return return_error(402, 'Gagal')

            data_out = {
                "code": 200,
                "status": "success",
                "data": {
                    "name": user.name,
                    "poin": user.poin,
                    "sedekah": user.sedekah,
                }
            }
            return data_out, 200
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return return_error(402, 'Error')

class UserSedekahRes(Resource):
    def post(self):
        try:
            waktu = datetime.now()
            data_rq = request.get_json(force=True)
            token_id = data_rq['token_id']
            sedekah = data_rq['sedekah']

            if not token_id:
                return return_error(402, 'Gagal')

            user = User.objects(id=token_id).first()
            if not user:
                return return_error(402, 'Gagal')

            user.sedekah = sedekah
            user.save()

            data_out = {
                "code": 200,
                "status": "success",
            }
            return data_out, 200
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return return_error(402, 'Error')