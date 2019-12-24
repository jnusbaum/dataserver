import os
import logging
from flask import Flask
from config import Config
from flask import jsonify, request
from views import *

app = Flask(__name__)
app.config.from_object(Config)

# set up logger
# make file unique
# we will be running multiple processes behind gunicorn
# we do not want all the processes writing to the same log file as this can result in garbled data in the file
# so we need a unique file name each time we run
# we will add date and time down to seconds (which will probably be the same for all processes)
# and add process id to get uniqueness
fparts = app.config['LOGFILE'].split('.')
bname = fparts[0]
ename = fparts[1]
nname = "%s.%s.%d.%s" % (bname, datetime.today().strftime("%Y-%m-%d-%H-%M-%S"), os.getpid(), ename)
logfile = app.config['LOGDIR'] + nname
# create log directory if it does not exist
os.makedirs(app.config['LOGDIR'], 0o777, True)
# set up basic logging
logging.basicConfig(filename=logfile, level=app.config['LOGLEVEL'],
                    format='%(asctime)s - %(levelname)s - %(message)s')


db.bind(provider='postgres', host=app.config['DBHOST'],
        database=app.config['DATABASE'],
        user=app.config['DBUSER'],
        password=app.config['DBPWD'],
        connect_timeout=300)

db.generate_mapping()


def str_to_datetime(ans):
    if ans:
        d = datetime.strptime(ans, "%Y-%m-%d-%H-%M-%S")
        # no tz info, assumed to be in UTC
        return d
    return None


class VIServiceException(Exception):
    def __init__(self, message, status_code):
        Exception.__init__(self, message)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        rv = {'error': self.message}
        return rv


class VI400Exception(VIServiceException):
    def __init__(self, message):
        super().__init__(message, 400)


class VI401Exception(VIServiceException):
    def __init__(self, message):
        super().__init__(message, 401)


class VI403Exception(VIServiceException):
    def __init__(self, message):
        super().__init__(message, 403)


class VI404Exception(VIServiceException):
    def __init__(self, message):
        super().__init__(message, 404)


class VI500Exception(VIServiceException):
    def __init__(self, message):
        super().__init__(message, 500)


def error_response(error, headers=None):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    if headers:
        response.headers = headers
    return response


@app.errorhandler(VIServiceException)
def handle_exception(error):
    rollback()
    return error_response(error)


@app.route('/', methods=['GET'])
def api_index():
    # return doc page
    return "Welcome to the sensor API"


@app.route('/sensors', methods=['GET', 'POST'])
@db_session
def api_sensors():
    if request.method == 'POST':
        # if POST add new sensor
        Sensor(name=request.form['name'], type=request.form['type'],
               address=request.form['address'], description=request.form['description'])
        return "", 201
    else:
        # if GET return list of sensors
        sensors = Sensor.select().sort_by(Sensor.name)
        rsensors = {'count': len(sensors), 'data': [SensorView.render(s) for s in sensors]}
        return jsonify(rsensors)


@app.route('/sensors/<sensor_name>', methods=['GET', 'PATCH', 'DELETE'])
@db_session
def api_sensor(sensor_name):
    if request.method == 'PATCH':
        # if PATCH add data for sensor
        try:
            sensor = Sensor[sensor_name]
        except ObjectNotFound:
            raise VI404Exception("No Sensor with the specified id was found.")
        # can't change pk (name)
        try:
            sensor.type = request.form['type']
        except KeyError:
            pass
        try:
            sensor.address = request.form['address']
        except KeyError:
            pass
        try:
            sensor.description = request.form['description']
        except KeyError:
            pass
        return "", 204
    elif request.method == 'DELETE':
        # if DELETE delete sensor
        try:
            sensor = Sensor[sensor_name]
        except ObjectNotFound:
            raise VI404Exception("No Sensor with the specified id was found.")
        sensor.delete()
        return "", 204
    else:
        # if GET get sensor meta data
        try:
            sensor = Sensor[sensor_name]
        except ObjectNotFound:
            raise VI404Exception("No Sensor with the specified id was found.")
        rsensor = {'count': 1, 'data': [SensorView.render(sensor)]}
        return jsonify(rsensor)


bool_values = {
    'on': True,
    'true': True,
    '1': True,
    'True': True,
    'off': False,
    'false': False,
    '0': False,
    'False': False
}


@app.route('/sensors/<sensor_name>/data', methods=['GET', 'POST'])
@db_session
# url options for GET
# targettime=<datetime: targettime> get data <= <targettime>, default is now
# datapts=<int: datapts> get <datapts> sensor reading back from target time, default is 1
# default is to get latest sensor reading for sensor
def api_sensor_data(sensor_name):
    if request.method == 'POST':
        # if POST add data for sensor
        timestamp = request.form.get('timestamp')
        if timestamp:
            timestamp = str_to_datetime(timestamp)
        else:
            timestamp = datetime.today()
        value_real = request.form.get('value-real')
        if value_real:
            value_real = Decimal(value_real)
        value_bool = request.form.get('value-bool')
        if value_bool:
            try:
                value_bool = bool_values[value_bool]
            except KeyError:
                # invalid bool value specified
                raise VI400Exception("Invalid bool value specified.")
        try:
            sensor = Sensor[sensor_name]
        except ObjectNotFound:
            raise VI404Exception("No Sensor with the specified id was found.")
        SensorData(sensor=sensor, timestamp=timestamp, value_real=value_real, value_bool=value_bool)
        return "", 201
    else:
        # if GET get data for sensor
        targettime = request.args.get('targettime', default=datetime.today(), type=str_to_datetime)
        datapts = request.args.get('datapts', default=1, type=int)
        try:
            sensor = Sensor[sensor_name]
        except ObjectNotFound:
            raise VI404Exception("No Sensor with the specified id was found.")
        sdata = sensor.data.filter(lambda s: s.timestamp <= targettime).order_by(desc(SensorData.timestamp)).limit(datapts)
        rsensordata = {'count': len(sdata), 'data': [SensorDataView.render(s) for s in sdata]}
        return jsonify(rsensordata)


@app.route('/sensors/<sensor_name>/data/<int:sensordata_id>', methods=['GET'])
@db_session
def api_sensor_data_by_id(sensor_name, sensordata_id):
    # if GET get data for sensor
    try:
        sensor = Sensor[sensor_name]
    except ObjectNotFound:
        raise VI404Exception("No Sensor with the specified id was found.")
    sdata = sensor.data.filter(id=sensordata_id)
    rsensordata = {'count': len(sdata), 'data': [SensorDataView.render(s) for s in sdata]}
    return jsonify(rsensordata)


if __name__ == '__main__':
    app.run(host=app.config['WWWHOST'],
            port=app.config['WWWPORT'])
    
