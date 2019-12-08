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
    data = Set('SensorData')

    def before_insert(self):
        if self.type not in ( 'TEMP', 'POS', 'ONOFF' ):
            raise TypeError("value for type must be one of TEMP, POS, ONOFF")

    def before_update(self):
        if self.type not in ( 'TEMP', 'POS', 'ONOFF' ):
            raise TypeError("value for type must be one of TEMP, POS, ONOFF")


class SensorData(db.Entity):
    id = PrimaryKey(int, auto=True)
    sensor = Required('Sensor')
    timestamp = Required(datetime)
    value_real = Optional(Decimal, precision=10, scale=2)
    value_bool = Optional(bool)

    def before_insert(self):
        if not (self.value_real or self.value_bool):
            raise TypeError("must have a real or boolean value specified")

    def before_update(self):
        if not (self.value_real or self.value_bool):
            raise TypeError("must have a real or boolean value specified")
