from enum import IntEnum
from app import db
from strenum import StrEnum
from mongoengine import fields


class AttendanceStatus(IntEnum):
    DIBATALKAN = 1
    AKAN_HADIR = 2
    HADIR = 3


class AttendanceType(StrEnum):
    TABLIGH_AKBAR = "TABLIGH_AKBAR"
    NGAJI_ASYIK = "NGAJI_ASYIK"
    NGAJI_AMIDA = "NGAJI_AMIDA"


class Attendance(db.Document):
    user_id = db.ObjectIdField()
    type = fields.EnumField(AttendanceType, default=AttendanceType.NGAJI_ASYIK)
    status = fields.EnumField(AttendanceStatus, default=AttendanceStatus.AKAN_HADIR)

    created    = db.DateTimeField()
    modified   = db.DateTimeField()