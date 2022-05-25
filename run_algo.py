# from algo import M_owm_api as owm_api
import M_owm_api as owm_api  # process_algo as process
import pandas
import os
from datetime import datetime

# -- main algo
# -- Simplified Algo
# until ML Algo has enough data
def run_algo_smplfd(dataset, lat, lon, stype):
    # data set consists out of six rows timestamp: 'dt'; temperature: 'temp'; humidity: 'humidity; dew point:
    # 'dew_point'; wind: 'wind'; weather id: 'weather_id'

    # last timestamp in data set
    newest = dataset.tail(1)

    # -- AVERAGE Values for the past 5 days
    # average temp (last 5 days)
    temp_avrg_5days = dataset['temp'].mean()
    print("Average Temp: " + str(temp_avrg_5days))

    # average humidity (last 5 days)
    hum_avrg_5days = dataset['humidity'].mean()
    print("Average Hum: " + str(hum_avrg_5days))

    # average wind
    wind_avrg_5days = dataset['wind'].mean()
    print("Average Wind: " + str(wind_avrg_5days))

    # -- RAIN INFO
    # find all time stamps with rain
    # initial filter by weather id and rain_mm
    rain = dataset.query('(weather_id >= 200) & (weather_id <= 700) & (rain_mm > 0.1)')
    print(rain)

    # information on all "rains"
    # ---
    # rain in the last 5 days in the data set
    if not rain.empty:
        # amount of rain last 5 days
        rain_commulated_5days = round(rain['rain_mm'].sum(),1)
        print("sum rain last 5 days:")
        print(rain_commulated_5days)

        # last rain / last row
        lastrain_row = rain.tail(1)

        # -- time since last rain
        # reference point "now" or timestamp of following rain
        ref_timestamp = int(datetime.now(tz=None).timestamp())

        # time since last rain / dataset newest value
        ts_diff_lastrain = (int(newest['dt']) - int(lastrain_row['dt']))
        print("timestamp last rain:")
        print(ts_diff_lastrain)
        ts_lastrain = int(lastrain_row['dt'])


        # -- detailed data for the latest rain
        # -- processed only if last rain is not now
        if ts_diff_lastrain != 0:
            # status bit = 1: there was rain in the past 5 days
            print("hell yeah")

            # time since rain until ref timestamp in hours
            # -1 because of 1 hour blocks in the data set
            time_since_rain = (ts_diff_lastrain / 3600) - 1
            time_since_rain_daysandhours = hoursindays(time_since_rain)
            time_since_rain_days = round(time_since_rain_daysandhours[0], 1)
            time_since_rain_hours = round(time_since_rain_daysandhours[1], 1)

            # temp since rain
            temp_since_rain = dataset.query('dt <= @ref_timestamp and dt >= @ts_lastrain')['temp'].mean()

            # wind since rain
            wind_since_rain = dataset.query('dt <= @ref_timestamp and dt >= @ts_lastrain')['wind'].mean()

            # humidity since rain
            hum_since_rain = dataset.query('dt <= @ref_timestamp and dt >= @ts_lastrain')['humidity'].mean()

            calc_cos_res = calc_cos_smplfd(time_since_rain_days, time_since_rain_hours, rain_commulated_5days,
                                           temp_since_rain, hum_since_rain, temp_avrg_5days, hum_avrg_5days, )

            rain_status = 1           # it's raining
            rain_commulated_5days = rain_commulated_5days
            time_since_rain_days = time_since_rain_days       # it's raining > 50
            time_since_rain_hours = time_since_rain_hours
            condition_road = 0 # VALUE NEEDS TO BE SET 1
            condition_gravel = 0 # VALUE NEEDS TO BE SET
            condition_trail = 0 # VALUE NEEDS TO BE SET

        if ts_diff_lastrain == 0:
            # it's raining, let's get dirty or shred on an other day!
            rain_status = 2            # it's raining
            rain_commulated_5days = rain_commulated_5days
            time_since_rain_days = 0        # it's raining > 50
            time_since_rain_hours = 0
            condition_road = 2 # VALUE NEEDS TO BE SET
            condition_gravel = 2 # VALUE NEEDS TO BE SET
            condition_trail = 2 # VALUE NEEDS TO BE SET

    else:
        # no rain
        rain_status = 0  # no rain
        rain_commulated_5days = 0
        time_since_rain_days = 99   # not relevant > 99
        time_since_rain_hours = 99
        condition_road = 0          # DRY: 0, DRY-WET: 1, Part
        condition_gravel = 0        # Dry
        condition_trail = 0         # DRY

    return {'rain_status': str(rain_status), 'time_since_rain_days': str(time_since_rain_days),
            'time_since_rain_hours': str(time_since_rain_hours), 'rain_commulated_l5days_mm': str(rain_commulated_5days),
            'temp_avrg': str(temp_avrg_5days),
            'cos_road': condition_road, 'cos_gravel': condition_gravel, 'cos_trail': condition_trail,
            'lat': str(lat), 'lon': str(lon), 'stype': stype}

def calc_cos_smplfd(time_since_rain_days, time_since_rain_hours, amount_rain,
                    temp_since_rain, hum_since_rain, temp_avrg, hum_avrg):

    ccos_gen = 1

    road_factor = 0
    gravel_factor = 0.8
    trail_factor = 0.5

    ccos_road = ccos_gen * road_factor
    ccos_gravel = ccos_gen * gravel_factor
    ccos_trail = ccos_gen * trail_factor

    return {'road': ccos_road, 'gravel': ccos_gravel, 'trail': ccos_trail}

# -- Alternative "hard coded" way
# depreciated (will be replaced by ML Algo)
def run_base_algo_detailed(dataset, lat, lon, stype):
    # data set consists out of six rows timestamp: 'dt'; temperature: 'temp'; humidity: 'humidity; dew point:
    # 'dew_point'; wind: 'wind'; weather id: 'weather_id'

    # last timestamp in data set
    newest = dataset.tail(1)

    # find all time stamps with rain
    # initial filter by weather id and rain_mm
    rain = dataset.query('(weather_id >= 200) & (weather_id < 700) & (rain_mm > 0.1)')
    print(rain)

    # information on all "rains"
    # ---
    # rain in the last 5 days in the data set
    if not rain.empty:
        # last rain / last row
        lastrain_row = rain.tail(1)
        print(lastrain_row)

        # -- time since really last rain
        # reference point "now" or timestamp of following rain
        ref_timestamp = int(datetime.now(tz=None).timestamp())

        # time since last rain
        ts_lastrain = (int(newest['dt']) - int(lastrain_row['dt']))
        print(ts_lastrain)

        # -- history of last 5 days:
        # -- average values
        # amount of rain last 5 days
        rain_commulated_l5days = round(rain['rain_mm'].sum(),1)
        print(rain_commulated_l5days)

        # average temp (last 5 days)
        temp_avrg_l5days = rain['temp'].mean()
        print(temp_avrg_l5days)

        # average humidity (last 5 days)
        hum_avrg_l5days = rain['humidity'].mean()

        # average wind
        wind_avrg_l5days = rain['wind'].mean()

        # -- detailed data for the latest rain
        # -- processed only if last rain is not now
        if ts_lastrain != 0:
            # status bit: there was rain in the past 5 days
            rain_status = 1

            # all data on the rain
            # get timestamp change is bigger than 3600
            col = ['dt_start', 'dt_end', 'weather_id', 'rain_duration', 'rain_intensity',
                   'time_since_prevrain', 'temp_since_rain', 'wind_since_rain', 'hum_since_rain']
            rain_data = pandas.DataFrame(columns=col)

            # overall last rain and additional info
            # end of last rain (overall)
            rain_end_ts = int(lastrain_row['dt'])
            rain_end_idx = rain.tail(1).index[0]

            # time since rain until ref timestamp in hours
            # -1 because of 1 hour blocks in the data set
            time_since_rain = ((ref_timestamp - rain_end_ts) / 3600) - 1
            time_since_rain = hoursindays(time_since_rain)
            time_since_rain_days = round(time_since_rain[0], 1)
            time_since_rain_hours = round(time_since_rain[1], 1)

            # temp since rain
            temp_since_rain = dataset.query('dt <= @ref_timestamp and dt >= @rain_end_ts')['temp'].mean()

            # wind since rain
            wind_since_rain = dataset.query('dt <= @ref_timestamp and dt >= @rain_end_ts')['wind'].mean()

            # humidity since rain
            hum_since_rain = dataset.query('dt <= @ref_timestamp and dt >= @rain_end_ts')['humidity'].mean()

            # determine rain duration and further "rain" in the time frame
            rain_len = rain.shape[0] - 1
            for row in range(rain_len, 0, -1):
                if row != 0:
                    if rain.iloc[row]['dt'] - rain.iloc[row-1]['dt'] > 3600:
                        # start of rain
                        rain_start_ts = rain.iloc[row]['dt']
                        # rain_start_idx = rain[rain['dt'] == rain.iloc[row]['dt']].index[0]

                        # rain duration
                        rain_duration = ((rain_end_ts - rain_start_ts) / 3600) + 1

                        # rain intensity
                        rain_intensity = rain.query('dt >= @rain_start_ts and dt <= @rain_end_ts')['rain_mm'].sum()

                        # rain object
                        rain_data = rain_data.append(
                            {'dt_start': rain_end_ts, 'dt_end': rain.iloc[row]['dt'],
                             'weather_id': rain.iloc[row]['weather_id'], 'rain_duration': round(rain_duration, 1),
                             'rain_intnsty': round(rain_intensity, 1)}, ignore_index=True)

                        # update rain_end with next "rain block" from data set and reference timestamp
                        rain_end_ts = rain.iloc[row-1]['dt']
                        ref_timestamp = rain_start_ts

                    # condition if rain is only 1 hour
                    elif (rain.iloc[row]['dt'] - rain.iloc[row-1]['dt'] == 3600) and (row == 1):
                        rain_start_ts = rain.iloc[row-1]['dt']

                        # rain duration
                        rain_duration = ((rain_end_ts - rain_start_ts) / 3600) + 1

                        # rain intensity
                        rain_intensity = rain.query('dt >= @rain_start_ts and dt <= @rain_end_ts')['rain_mm'].sum()

                        # rain object
                        rain_data = rain_data.append(
                            {'dt_start': rain_end_ts, 'dt_end': rain.iloc[row]['dt'],
                             'weather_id': rain.iloc[row]['weather_id'], 'rain_duration': round(rain_duration, 1),
                             'rain_intnsty': round(rain_intensity, 1)}, ignore_index=True)

                        # update rain_end with next "rain block" from data set and reference timestamp
                        rain_end_ts = rain.iloc[row-1]['dt']
                        ref_timestamp = rain_start_ts
            if rain_len == 0:
                rain_duration = 1
                rain_intensity = rain.query('dt == @rain_end_ts')['rain_mm'].sum()
                # rain object
                rain_data = rain_data.append(
                    {'dt_start': rain_end_ts, 'dt_end': rain_end_ts,
                     'weather_id': rain.query('dt == @rain_end_ts')['weather_id'], 'rain_duration': round(rain_duration, 1),
                     'rain_intnsty': round(rain_intensity, 1)}, ignore_index=True)

            # duration of last rain - MVP - only consider last rain and its duration
            if not rain_data.empty:
                lastrain_duration = round(float(rain_data.head(1)['rain_duration']),2)
                lastrain_intensity = round(float(rain_data.head(1)['rain_intnsty']),2)

        elif ts_lastrain == 0:
            # it's raining, let's get dirty or shred on an other day!
            rain_status = 50            # it's raining > 50
            rain_commulated_l5days = rain_commulated_l5days
            time_since_rain_days = 0        # it's raining > 50
            time_since_rain_hours = 0
            lastrain_duration = 0      # not relevant > 99
            lastrain_intensity = 0     # not relevant > 99
            temp_avrg_l5days = 0
            wind_avrg_l5days = 0
            hum_avrg_l5days = 0

    else:
        # no rain in the past 5 days
        rain_status = 0  # no rain > 0
        rain_commulated_l5days = 0
        time_since_rain_days = 99  # not relevant > 99
        time_since_rain_hours = 99
        lastrain_duration = 99  # not relevant > 99
        lastrain_intensity = 99  # not relevant > 99
        temp_avrg_l5days = 99
        wind_avrg_l5days = 99
        hum_avrg_l5days = 99

    cos = calc_cos(rain_status, time_since_rain_days, time_since_rain_hours, lastrain_intensity, rain_commulated_l5days,
                     temp_avrg_l5days, wind_avrg_l5days, hum_avrg_l5days)

    return {'rain_status': str(rain_status), 'time_since_rain_days': str(time_since_rain_days),
            'time_since_rain_hours': str(time_since_rain_hours), 'lastrain_duration_h': str(lastrain_duration),
            'lastrain_intensity_mm': str(lastrain_intensity), 'rain_commulated_l5days_mm': str(rain_commulated_l5days),
            'cos_road': cos['road'], 'cos_gravel': cos['gravel'], 'cos_trail': cos['trail'],
            'lat': str(lat), 'lon': str(lon), 'stype': stype}

def calc_cos(rain_status, time_since_rain_days, time_since_rain_hours, lastrain_intensity, amount_of_rain, avrg_temp, avrg_wind, avrg_hum):
    # init of needed dicts and parameters
    diff_dry_time_dict = {}
    cos = {}
    key = ["road", "gravel", "trail"]
    it = 0
    f_roadfaktor = 0.5
    f_trailfaktor = -0.1

    # look up table for environment paramets with influence on dry time
    # trimed for gravel surface
    lookup_temp = { -2: 0.1041, -1: 0.1111, 0: 0.1111, 1: 0.1190, 2: 0.1388, 3: 0.1667, 4: 0.2083}
    lookup_hum = { 3: 0.02, 4: 0.01, 5: 0.01, 6: 0.0, 7: -0.02}
    lookup_sun = {0: 0, 2: 0.01, 4: 0.02, 6: 0.03, 8: 0.04, 10: 0.04 }

    # look up of temp factor (f)
    # simplified look up via first int digit as string
    str_avrg_temp_full = str(round(avrg_temp))
    print("Temp:" + str(avrg_temp))
    str_avrg_temp = str_avrg_temp_full[0]
    if str_avrg_temp == "-":
        str_avrg_temp = str_avrg_temp_full[0] + str_avrg_temp_full[1]
        int_avrg_temp = int(str_avrg_temp)
    else:
        int_avrg_temp = int(str_avrg_temp)
    if int_avrg_temp < -2:
        int_avrg_temp = -2
    elif int_avrg_temp > 4:
        int_avrg_temp = 4
    f_temp = lookup_temp[int_avrg_temp]

    # look up of humidity factor (f)
    # simplified str look up over first digit of averg humditiy
    str_avrg_hum = str(round(avrg_hum))
    str_avrg_hum = int(str_avrg_hum[0])
    if str_avrg_hum <= 3:
        str_avrg_hum = 3
    elif str_avrg_hum >= 7:
        str_avrg_hum = 7
    f_hum = lookup_hum[str_avrg_hum]

    # sum of all factors for each roadtype
    f_sum_gravel = f_temp # f_hum
    f_sum_road = f_temp + f_roadfaktor
    f_sum_trail = f_temp + f_trailfaktor

    # f_sum list of all factors
    f_sum =  [f_sum_road, f_sum_gravel, f_sum_trail]

    # time since last rain in hours
    time_since_rain = round((time_since_rain_days * 24), 1) + time_since_rain_hours

    # diff between dry time and time since last rain
    for f in f_sum:
        # equation: 0 = -sum_lookup * time_till_dry + amount_of_rain_l5days
        # time till surface is dry under given parameters aka factors (f)
        dry_time = -(lastrain_intensity) / -(f)
        print(f)

        # diff between time since last rain and needed time 2 dry "dry_time"
        if dry_time != 0:
            diff_dry_time = round(time_since_rain / dry_time, 1)
            print("drytime:" + str(diff_dry_time))
        else:
            diff_dry_time = 1

        #store for every surface type
        diff_dry_time_dict[key[it]] = diff_dry_time
        it = it+1

    # category cluster
    for time in diff_dry_time_dict:
        if diff_dry_time_dict[time] >= 1:
            cos[time] = "dry"
        elif diff_dry_time_dict[time]  >= 0.75:
            cos[time] = "mostly dry"
        elif diff_dry_time_dict[time]  >= 0.4:
            cos[time] = "mostly wet"
        elif diff_dry_time_dict[time]  < 0.4:
            cos[time] = "wet"
        else:
            cos[time] = "n/a"

    return cos

# -- get weather data
def get_owm_data(lat, lon, timestamp):
    # get hist data from owm
    owm_hist_dataset_return = owm_api.owm_hist_data(timestamp, lat, lon)

    return owm_hist_dataset_return


# -- main start point from website
# lat, lon, stype received from website
def mainloop (lat, lon, stype):

    # get current timestamp in UNIX
    timestamp = owm_api.time_now_UNIX()

    # get weather data
    weather_data_owm = get_owm_data(lat, lon, timestamp)

    # run the algo
    surface_condition = run_base_algo_detailed(weather_data_owm, lat, lon, stype)

    return surface_condition


# duration in minutes converted in to days, hours
def hoursindays(duration):
    days = duration / 24
    hours = duration - (24*days)

    return days, hours