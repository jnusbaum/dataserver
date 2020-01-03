from datetime import datetime
from decimal import *
from pony.orm import *

db = Database()


# Create your models here.
class Sensor(db.Entity):
    name = PrimaryKey(str)
    type = Required(str, max_len=8)
    address = Optional(str, max_len=128)
    description = Optional(str, max_len=512)
    zone = Optional('Zone', index=True)
    data = Set('SensorData')
    hour_bad = Optional(int)
    day_bad = Optional(int)
    ten_day_bad = Optional(int)

    def before_insert(self):
        if self.type not in ('TEMP', 'POS', 'ONOFF'):
            raise TypeError("value for type must be one of TEMP, POS, ONOFF")

    def before_update(self):
        if self.type not in ('TEMP', 'POS', 'ONOFF'):
            raise TypeError("value for type must be one of TEMP, POS, ONOFF")


class Zone(db.Entity):
    name = PrimaryKey(str)
    description = Optional(str, max_len=512)
    sensors = Set(Sensor)


class SensorData(db.Entity):
    id = PrimaryKey(int, auto=True)
    sensor = Required(Sensor)
    timestamp = Required(datetime)
    value_real = Required(Decimal, precision=10, scale=2)
    original_value = Optional(Decimal, precision=10, scale=2)
    composite_index(sensor, timestamp)

