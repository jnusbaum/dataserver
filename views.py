from models import *


class SensorView:
    @classmethod
    def render(cls, sensor: Sensor):
        dself = {'attributes': { 'type': sensor.type,
                                 'address': sensor.address,
                                 'description': sensor.description
                                },
                 'id': sensor.name,
                 'type': 'Sensor',
                 'self': f"/sensors/{sensor.name}",
                 'relationships': {
                     'data': f"/sensors/{sensor.name}/data"
                     }
                 }
        return dself


class SensorDataView:
    @classmethod
    def render(cls, sensordata: SensorData, altvalue: Decimal = None):
        dself = {'attributes': { 'timestamp': sensordata.timestamp.strftime("%Y-%m-%d-%H-%M-%S"),
                                 # this is a decimal so we convert it to a string here
                                 'value_real': str(altvalue if altvalue else sensordata.value_real),
                                 'value_bool': sensordata.value_bool,
                                },
                 'id': str(sensordata.id),
                 'type': 'SensorData',
                 'self': f"/sensors/{sensordata.sensor.name}/data/{sensordata.id}",
                 'relationships': {
                     'sensor': f"/sensors/{sensordata.sensor.name}"
                     }
                 }
        return dself
