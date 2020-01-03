from models import *
from statistics import mean
from datetime import timedelta

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
        # get 10 days of data
        n = datetime.today()
        tstart = n - timedelta(days=10)
        dstart = n - timedelta(days=1)
        hstart = n - timedelta(hours=1)
        bad10day = 0
        bad1day = 0
        bad1hr = 0
        sdata = sensor.data.filter(lambda sd: sd.timestamp >= tstart).sort_by(SensorData.timestamp)[:]
        if len(sdata) < 4:
            continue
        # initialize algorithm
        # determine if initial value is bad
        val = sdata[0].value_real
        avgval = mean((val, sdata[1].value_real, sdata[2].value_real, sdata[3].value_real))
        if val < MIN_TEMP or abs(val - avgval) > MAX_TEMP_MOVE:
            # bad value
            bad10day += 1
            # print(f"{sensor.name}: replacing {val} with {avgval} at index 0, timestamp {sdata[0].timestamp}")
            print(f"{sensor.name}: bad value {val} at index 0, timestamp {sdata[0].timestamp}")
            # sdata[0].original_value = val
            # sdata[0].value_real = avgval
        for i in range(1, len(sdata)):
            # null all clearly bad values
            prev = val
            itm = sdata[i]
            val = itm.value_real
            if val < MIN_TEMP or abs(val - prev) > MAX_TEMP_MOVE:
                bad10day += 1
                if itm.timestamp > dstart:
                    bad1day += 1
                if itm.timestamp > hstart:
                    bad1hr += 1
                # print(f"{sensor.name}: replacing {val} with {prev} at index {i}, timestamp {sdata[i].timestamp}")
                print(f"{sensor.name}: bad value {val} with {prev} at index {i}, timestamp {itm.timestamp}")
                val = prev
                # itm.original_value = itm.value_real
                # itm.value_real = val
        sensor.hour_bad = bad1hr
        sensor.day_bad = bad1day
        sensor.ten_day_bad = bad10day
        # commit each sensor
        print(f"{sensor.name}: {bad10day} bad data points out of {len(sdata)} in the last 10 days")
        print(f"{sensor.name}: {bad1day} bad data points in the last day")
        print(f"{sensor.name}: {bad1hr} bad data points in the last hour")
        commit()




