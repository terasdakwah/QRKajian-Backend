import textwrap
from datetime import datetime, timedelta
import traceback 
from flask_restful import Resource, url_for, request
from app.mod_apisv1.common.utils import string_datetime, return_error
from app.mod_user.models import User
from app.mod_attendance.models import Attendance, AttendanceStatus
from mongoengine.queryset.visitor import Q

class FillAttendanceRes(Resource):
    def post(self):
        try:
            waktu = datetime.now()
            data_rq = request.get_json(force=True)
            token_id = data_rq['token_id']
            qr_data = data_rq['qr_data']

            x = qr_data.split("#")
            attendance_type = x[1]

            if not token_id:
                return return_error(200, 'Gagal')

            user = User.objects(id=token_id).first()
            if not user:
                return return_error(200, 'Tidak terdaftar')

            dt_awal = datetime.now() - timedelta(hours=5)
            dt_akhir = datetime.now()

            user_name = textwrap.shorten(user.name, width=10, placeholder="..")
            attendance = Attendance.objects(user_id=user.id).filter(Q(created__gte=dt_awal) & Q(created__lte=dt_akhir)).first()
            if attendance:
                return return_error(200, "Hai %s Poin kamu: %s" % (user_name, user.poin,))

            attendance = Attendance()
            attendance.user_id = user.id
            attendance.status = AttendanceStatus.HADIR
            attendance.type = attendance_type
            attendance.created = datetime.now()
            attendance.modified = datetime.now()
            attendance.save()

            user.poin = user.poin + 1
            user.save()
            return return_error(200, "Selamat datang di Teras Dakwah<br />Semangat Ngajinyaa kak %s ~" % (user_name, ))
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return return_error(402, 'Error')