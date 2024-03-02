import io
import json
import xlsxwriter
import datetime as datetimex
from flask import Blueprint, render_template, request, \
                  flash, g, session, redirect, url_for, abort, redirect, send_file

from flask_paginate import Pagination
from datetime import datetime, timedelta
from app import db
from app.mod_user.forms import LoginForm, RegisterForm
from app.mod_attendance.models import Attendance
from app.mod_user.models import User, Provinces, Regencies, Districts
from werkzeug.security import check_password_hash, generate_password_hash
from mongoengine.queryset.visitor import Q
from app.utils.helper import allowed_file_image, string_date, calculateAge

mod_user = Blueprint('user', __name__, url_prefix='/')

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)  # this will never fail
    return next_month - timedelta(days=next_month.day)

@mod_user.route('/', methods=['GET', 'POST'])
def index():
    no_hp = session.get('no_hp')
    if not no_hp:
        return redirect(url_for('user.register'))

    page = request.args.get('page')
    if not page:
        page = 1
    page = int(page)

    per_page = request.args.get('per_page')
    if not per_page:
        per_page = 10
    per_page = int(per_page)

    list_user = []
    filtersedekah = request.args.get('sedekah', 0)
    filtermonth = request.args.get('month')
    if filtermonth:
        filtermonth = int(filtermonth)
        dt_awal = datetime(datetime.now().year, filtermonth, 1, hour = 0, minute = 0, second = 0)
        dt_akhir = last_day_of_month(datetime(datetime.now().year, filtermonth, 1, hour = 23, minute = 59, second = 59))
        if filtersedekah == 1:
            _user = User.objects(sedekah=True).order_by("-id").filter(Q(created__gte=dt_awal) & Q(created__lte=dt_akhir)).paginate(page=page, per_page=per_page)
        else:
            _user = User.objects.order_by("-id").filter(Q(created__gte=dt_awal) & Q(created__lte=dt_akhir)).paginate(page=page, per_page=per_page)
    else:
        if filtersedekah == 1:
            _user = User.objects(sedekah=True).order_by("-id").paginate(page=page, per_page=per_page)
        else:
            _user = User.objects.order_by("-id").paginate(page=page, per_page=per_page)

    for user in _user.items:
        dt_awal = datetime(datetime.now().year, datetime.now().month, 1, hour = 0, minute = 0, second = 0)
        dt_akhir = last_day_of_month(datetime(datetime.now().year, datetime.now().month, 1, hour = 23, minute = 59, second = 59))

        num_attendance = Attendance.objects(user_id=user.id).filter(Q(created__gte=dt_awal) & Q(created__lte=dt_akhir)).count()
        total_attendance = Attendance.objects(user_id=user.id).count()
        provinsi = ""
        kabupaten = ""
        kecamatan = ""

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

        is_sedekah = "BELUM"
        if user.sedekah:
            is_sedekah = "YA"

        list_user.append({
            "user_id" : str(user.id),
            "nama" : str(user.name),
            "jeniskelamin" : str(user.gender),
            "no_hp" : str(user.no_hp),
            "tipe" : str(user.tipe),
            "created": user.created,
            "num_attendance": num_attendance,
            "total_attendance": total_attendance,
            "poin": str(user.poin),
            "provinsi" : str(provinsi),
            "kabupaten" : str(kabupaten),
            "kecamatan" : str(kecamatan),
            "tgllahir": string_date(user.tanggallahir),
            "usia": calculateAge(user.tanggallahir),
            "pekerjaan": str(user.pekerjaaan),
            "instansi": str(user.instansi),
            "hobi": str(user.hobi),
            "sedekah": is_sedekah,
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
        worksheet.write(0,4, 'Kehadiran bulan ini')
        worksheet.write(0,5, 'Total Kehadiran')
        worksheet.write(0,6, 'Poin')

        worksheet.write(0,7, 'Provinsi')
        worksheet.write(0,8, 'Kabupaten')
        worksheet.write(0,9, 'Kecamatan')
        
        worksheet.write(0,10, 'Tanggal lahir')
        worksheet.write(0,11, 'Usia')
        worksheet.write(0,12, 'Pekerjaaan')
        worksheet.write(0,13, 'Instansi')
        worksheet.write(0,14, 'Hobi')
        worksheet.write(0,15, 'Waktu mendaftar')
        worksheet.write(0,16, 'Sedekah')
        row = 0
        col = 0
        for user in list_user:
            row = row + 1
            worksheet.write(row, col+0, row)
            worksheet.write(row, col+1, user['nama'])
            worksheet.write(row, col+2, user['jeniskelamin'])
            worksheet.write(row, col+3, user['no_hp'])
            worksheet.write(row, col+4, user['num_attendance'])
            worksheet.write(row, col+5, user['total_attendance'])
            worksheet.write(row, col+6, user['poin'])

            worksheet.write(row, col+7, user['provinsi'])
            worksheet.write(row, col+8, user['kabupaten'])
            worksheet.write(row, col+9, user['kecamatan'])

            worksheet.write(row, col+10, user['tgllahir'])
            worksheet.write(row, col+11, user['usia'])
            worksheet.write(row, col+12, user['pekerjaan'])
            worksheet.write(row, col+13, user['instansi'])
            worksheet.write(row, col+14, user['hobi'])

            worksheet.write(row, col+15, user['created'])
            worksheet.write(row, col+16, user['sedekah'])

        workbook.close()
        output.seek(0)
        fileNameExport = "data_jamaah_%s.xls" % (dt_now)
        return send_file(output, attachment_filename=fileNameExport, as_attachment=True)

    pagination = Pagination(css_framework='foundation', page=page,per_page=per_page,total=_user.total)
    data = {
        "pagination": pagination,
        "list_user": list_user,
        "current_month": datetime.now().month
    }
    return render_template("user/user.html", data=data)

@mod_user.route('/poin', methods=['GET', 'POST'])
def poin():
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

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        jumlahtukar = int(request.form.get('jumlahtukar'))

        if user_id and jumlahtukar:
            user = User.objects(id=user_id).first()
            if user:
                poinfinal = user.poin - jumlahtukar
                if poinfinal >= 0:
                    user.poin = poinfinal
                    user.save()
                    flash('Poin %s berhasil dikurangi %s' % (user.name, jumlahtukar), 'success')
                else:
                    flash('Poin %s kurang dari %s' % (user.name, jumlahtukar), 'error')

    search = request.args.get('search')
    list_user = []
    if search:
        _user = User.objects(no_hp=search).order_by("-poin").paginate(page=page, per_page=per_page)
    else:
        _user = User.objects.order_by("-poin").paginate(page=page, per_page=per_page)

    for user in _user.items:
        provinsi = ""
        kabupaten = ""
        kecamatan = ""

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
            "tipe" : str(user.tipe),
            "created": user.created,
            "poin": str(user.poin),
            "provinsi" : str(provinsi),
            "kabupaten" : str(kabupaten),
            "kecamatan" : str(kecamatan),
            "tgllahir": string_date(user.tanggallahir),
            "usia": calculateAge(user.tanggallahir),
            "pekerjaan": str(user.pekerjaaan)
        })

    pagination = Pagination(css_framework='foundation', page=page,per_page=per_page,total=_user.total)
    data = {
        "pagination": pagination,
        "list_user": list_user
    }
    return render_template("user/user_poin.html", data=data)

@mod_user.route('/login', methods=['GET', 'POST'])
def login():
    data = {}
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(no_hp=form.no_hp.data).first()
        if user and check_password_hash(user.password, form.password.data):
            if user.tipe == 3:
                session['no_hp'] = user.no_hp
                return redirect(url_for('user.index'))
            else:
                flash('Anda tidak berhak mengakses halaman ini.', 'error')
        else:
            flash('no. hp atau password salah', 'error')

    return render_template("user/login.html", data=data, form=form)

@mod_user.route('/register', methods=['GET', 'POST'])
def register():
    data = {}
    form = RegisterForm()

    name = form.name.data
    no_hp = form.no_hp.data
    tanggallahir = form.tanggallahir.data
    gender = form.gender.data

    provinsi = form.provinsi.data
    kabupaten = form.kabupaten.data
    kecamatan = form.kecamatan.data

    pekerjaaan = form.pekerjaaan.data
    instansi = form.instansi.data
    hobi = form.hobi.data

    sessi_uid = session.get('uid')
    if sessi_uid:
        return redirect(url_for('user.registerSuccess'))

    if request.method == 'POST':
        if name and no_hp and tanggallahir and gender and provinsi and kabupaten and kecamatan and pekerjaaan and instansi and hobi:
            user = User.objects(no_hp=no_hp).first()
            if not user:
                _user = form.save()
                session['uid'] = str(_user.id)
                flash('Berhasil disimpan', 'success')
                return redirect(url_for('user.registerSuccess'))
            else:
                session['uid'] = str(user.id)
                flash('No. Telpon Sudah terdaftar', 'error')
                return redirect(url_for('user.registerSuccess'))
        else:
            flash('Error : Coba lagi, silakan isi semua pilihan dengan benar', 'error')

    return render_template("user/register.html", data=data, form=form)

@mod_user.route('/register/success', methods=['GET', 'POST'])
def registerSuccess():
    sessi_uid = session.get('uid')
    if not sessi_uid:
        return redirect(url_for('user.register'))

    data = {
        "uid": str(sessi_uid)
    }
    return render_template("user/register_success.html", data=data)

@mod_user.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('user.login'))

@mod_user.route('/get_kab/<id>', methods=['GET'])
def get_kab(id):
    data = [{'id': '', 'name': 'Kabupaten/Kota'}]
    if id != "":
        regencies = Regencies.objects(province=id).limit(100)
        for regency in regencies:
            data.append({'id': str(regency.id), 'name': regency.name})
    return json.dumps(data)

@mod_user.route('/get_kec/<id>', methods=['GET'])
def get_kec(id):
    data = [{'id': '', 'name': 'Kecamatan'}]
    if id != "":
        districts = Districts.objects(regency=id).limit(100)
        for datax in districts:
            data.append({'id': str(datax.id), 'name': datax.name})
    return json.dumps(data)
