from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
from datetime import datetime
from app.mod_user.models import User, Provinces
from werkzeug.security import check_password_hash, generate_password_hash

def getprovdt():
    data = []
    provinces = Provinces.objects.limit(100)
    for province in provinces:
        data.append((province.id, province.name))
    return data

class LoginForm(FlaskForm):
    no_hp    = StringField('No. Hp', [DataRequired(message='Nomor HP wajib diisi')])
    password = PasswordField('Password', [DataRequired(message='Password wajib diisi')])


class RegisterForm(FlaskForm):
    name     = StringField('Nama', [DataRequired(message='Nama wajib diisi')])
    no_hp    = StringField('No. Hp', [DataRequired(message='Nomor HP wajib diisi')])
    tanggallahir  = StringField('Tanggal lahir', [DataRequired(message='Tanggal lahir wajib diisi')])
    gender   = SelectField(
        'Jenis kelamin', choices=[('L', 'Pria'), ('P', 'Wanita')]
    )

    provinsi = SelectField('Provinsi', [DataRequired(message='wajib diisi')], choices = getprovdt())
    kabupaten = SelectField('Kabupaten', choices = [])
    kecamatan = SelectField('Kecamatan', choices = [])

    pekerjaaan = SelectField('Pekerjaan', [DataRequired(message='Pekerjaan wajib diisi')], choices = [])
    instansi  = StringField('Instansi', [DataRequired(message='Instansi wajib diisi')])
    hobi  = StringField('Hobi', [DataRequired(message='Hobi wajib diisi')])

    instance = None
    document_class = User

    def __init__(self, document=None, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

    def save(self):
        waktu = datetime.now()
        if self.instance is None:
            self.instance = self.document_class()
            created = waktu
        else:
            created = self.instance.created

        self.instance.name = self.name.data
        self.instance.no_hp = self.no_hp.data
        self.instance.tanggallahir = datetime.strptime(self.tanggallahir.data, "%d/%m/%Y")
        self.instance.gender = self.gender.data
        self.instance.provinsi = self.provinsi.data
        self.instance.kabupaten = self.kabupaten.data
        self.instance.kecamatan = self.kecamatan.data
        self.instance.pekerjaaan = self.pekerjaaan.data
        self.instance.instansi = self.instansi.data
        self.instance.hobi = self.hobi.data
        self.instance.password = generate_password_hash('12345')

        self.instance.created = created
        self.instance.modified = waktu

        self.instance.save()
        return self.instance