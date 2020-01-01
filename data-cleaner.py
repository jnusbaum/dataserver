from models import *
from statistics import mean

MAX_TEMP_MOVE = 25
MIN_TEMP = 30

db.bind(provider='postgres', host='192.168.0.134',
        database='automation',
        user='rjn',
        password='zaxxon')

db.generate_mapping()

# clean sensor data

with db_session():
    sensors = Sensor.select()
    for sensor in sensors:
        bad = 0
        sdata = sensor.data.sort_by(SensorData.timestamp)[:]
        if len(sdata) < 4:
            continue
        # initialize algorithm
        # determine if initial value is bad
        val = sdata[0].value_real
        avgval = mean((val, sdata[1].value_real, sdata[2].value_real, sdata[3].value_real))
        if val < MIN_TEMP or abs(val - avgval) > MAX_TEMP_MOVE:
            # bad value
            bad += 1
            print(f"{sensor.name}: replacing {val} with {avgval} at index 0, timestamp {sdata[0].timestamp}")
            sdata[0].original_value = val
            sdata[0].value_real = avgval
        for i in range(1, len(sdata)):
            # null all clearly bad values
            prev = val
            val = sdata[i].value_real
            if val < MIN_TEMP or abs(val - prev) > MAX_TEMP_MOVE:
                bad += 1
                print(f"{sensor.name}: replacing {val} with {prev} at index {i}, timestamp {sdata[i].timestamp}")
                val = prev
                sdata[i].original_value = sdata[i].value_real
                sdata[i].value_real = val
        # commit each sensor
        print(f"{sensor.name}: {bad} bad data points out of {len(sdata)}")
        # commit()
    rollback()



