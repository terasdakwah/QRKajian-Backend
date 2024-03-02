import io
import json
import xlsxwriter
import datetime as datetimex
from flask import Blueprint, render_template, request, \
                  flash, g, session, redirect, url_for, abort, redirect, send_file

from flask_paginate import Pagination
from datetime import datetime, timedelta
from app import db
from app.mod_attendance.models import Attendance
from app.mod_user.models import User, Provinces, Regencies, Districts
from werkzeug.security import check_password_hash, generate_password_hash
from mongoengine.queryset.visitor import Q
from app.utils.helper import allowed_file_image, string_date, calculateAge

mod_attendance = Blueprint('attendance', __name__, url_prefix='/attendance')

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)  # this will never fail
    return next_month - timedelta(days=next_month.day)

@mod_attendance.route('/', methods=['GET', 'POST'])
def index():
    no_hp = session.get('no_hp')
    if not no_hp:
        return redirect(url_for('user.login'))

    page = request.args.get('page')
    if not page:
        page = 1
    page = int(page)

    per_page = request.args.get('per_page')
    if not per_page:
        per_page = 10
    per_page = int(per_page)

    list_user = []
    start = request.args.get('start')
    end = request.args.get('end')
    type = request.args.get('type', "1010")

    if start and end:
        start = datetime.strptime(start, "%d/%m/%Y")
        end = datetime.strptime(end, "%d/%m/%Y")

    if type == "1010":
        if start and end:
            dt_awal = datetime(start.year, start.month, start.day, hour = 0, minute = 0, second = 0)
            dt_akhir = datetime(end.year, end.month, end.day, hour = 23, minute = 59, second = 59)
            _attendance = Attendance.objects.order_by("-id").filter(Q(created__gte=dt_awal) & Q(created__lte=dt_akhir)).paginate(page=page, per_page=per_page)
        else:
            _attendance = Attendance.objects.order_by("-id").paginate(page=page, per_page=per_page)

    else:
        if start and end:
            dt_awal = datetime(start.year, start.month, start.day, hour = 0, minute = 0, second = 0)
            dt_akhir = datetime(end.year, end.month, end.day, hour = 23, minute = 59, second = 59)
            _attendance = Attendance.objects(type=type).order_by("-id").filter(Q(created__gte=dt_awal) & Q(created__lte=dt_akhir)).paginate(page=page, per_page=per_page)
        else:
            _attendance = Attendance.objects(type=type).order_by("-id").paginate(page=page, per_page=per_page)


    for attendance in _attendance.items:
        provinsi = ""
        kabupaten = ""
        kecamatan = ""
        user = User.objects(id=attendance.user_id).first()

        if user.provinsi:
            _provinsi = Provinces.objects(id=user.provinsi).first()
            if _provinsi:
                provinsi = _provinsi.name
        if user.kabupaten:
            _kabupaten = Regencies.objects(id=user.kabupaten).first()
            if _kabupaten:
                kabupaten = _kabupaten.name
        if user.kecamatan:
            _kecamatan = Districts.objects(id=user.kecamatan).first()
            if _kecamatan:
                kecamatan = _kecamatan.name

        list_user.append({
            "user_id" : str(user.id),
            "nama" : str(user.name),
            "jeniskelamin" : str(user.gender),
            "no_hp" : str(user.no_hp),
            "kajian" : str(attendance.type),
            "created": str(attendance.created),
            "poin": str(user.poin),
            "provinsi" : str(provinsi),
            "kabupaten" : str(kabupaten),
            "kecamatan" : str(kecamatan),
            "tgllahir": string_date(user.tanggallahir),
            "usia": calculateAge(user.tanggallahir),
            "pekerjaan": str(user.pekerjaaan),
            "instansi": str(user.instansi),
            "hobi": str(user.hobi)
        })

    if request.args.get('export') == 'true':
        dt_now = datetime.now()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'default_date_format':'dd/mm/yy', 'in_memory': True})
        worksheet = workbook.add_worksheet()

        worksheet.write(0,0, 'No')
        worksheet.write(0,1, 'Nama')
        worksheet.write(0,2, 'Jenis Kelamin')
        worksheet.write(0,3, 'No Hp')
        worksheet.write(0,4, 'Kajian')

        worksheet.write(0,5, 'Provinsi')
        worksheet.write(0,6, 'Kabupaten')
        worksheet.write(0,7, 'Kecamatan')
        
        worksheet.write(0,8, 'Tanggal lahir')
        worksheet.write(0,9, 'Usia')
        worksheet.write(0,10, 'Pekerjaaan')
        worksheet.write(0,11, 'Instansi')
        worksheet.write(0,12, 'Hobi')

        worksheet.write(0,13, 'Waktu Hadir')
        row = 0
        col = 0
        for user in list_user:
            row = row + 1
            worksheet.write(row, col+0, row)
            worksheet.write(row, col+1, user['nama'])
            worksheet.write(row, col+2, user['jeniskelamin'])
            worksheet.write(row, col+3, user['no_hp'])
            worksheet.write(row, col+4, user['kajian'])

            worksheet.write(row, col+5, user['provinsi'])
            worksheet.write(row, col+6, user['kabupaten'])
            worksheet.write(row, col+7, user['kecamatan'])

            worksheet.write(row, col+8, user['tgllahir'])
            worksheet.write(row, col+9, user['usia'])
            worksheet.write(row, col+10, user['pekerjaan'])
            worksheet.write(row, col+11, user['instansi'])
            worksheet.write(row, col+12, user['hobi'])

            worksheet.write(row, col+13, user['created'])

        workbook.close()
        output.seek(0)
        fileNameExport = "data_presensi_%s.xls" % (dt_now)
        return send_file(output, download_name=fileNameExport, as_attachment=True)

    pagination = Pagination(css_framework='foundation', page=page,per_page=per_page,total=_attendance.total)
    data = {
        "pagination": pagination,
        "list_user": list_user,
        "current_month": datetime.now().month
    }
    return render_template("attendance/attendance.html", data=data)
