# from algo
from algo import M_owm_api as owm_api  # process_algo as process
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import pandas
from datetime import datetime


# main algo
def run_base_algo(dataset, lat, lon, stype):
    # data set consists out of six rows timestamp: 'dt'; temperature: 'temp'; humidity: 'humidity; dew point:
    # 'dew_point'; wind: 'wind'; weather id: 'weather_id'

    # last timestamp in data set
    newest = dataset.tail(1)

    # find all time stamps with rain
    rain = dataset.query('(weather_id >= 200) & (weather_id < 700) & (rain_mm > 0.2)')
    print(rain)

    # information on all "rains"
    # ---
    if not rain.empty:
        # last rain / last row
        lastrain_row = rain.tail(1)

        # short cut if last rain is really long ago
        # time since really last rain
        # reference point "now" or timestamp of following rain
        ref_timestamp = int(datetime.now(tz=None).timestamp())

        ts_lastrain = (int(newest['dt']) - int(lastrain_row['dt']))

        rain_commulated_l5days = round(rain['rain_mm'].sum(),1)
        temp_avrg_l5days = rain['temp'].mean()
        hum_avrg_l5days = rain['humidity'].mean()
        wind_avrg_l5days = rain['wind'].mean()

        # if last rain is below threshold do the math
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
        # no rain
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


# main start point from website
# lat, lon, stype received from website
def mainloop (lat, lon, stype):

    # get current timestamp in UNIX
    timestamp = owm_api.time_now_UNIX()

    weather_data_owm = get_owm_data(lat, lon, timestamp)

    # calc trail condition algo and calc condition of surface (cos)
    surface_condition = run_base_algo(weather_data_owm, lat, lon, stype)

    return surface_condition


def get_owm_data(lat, lon, timestamp):
    # get hist data from owm
    owm_hist_dataset_return = owm_api.owm_hist_data(timestamp, lat, lon)

    # read in test data
    # owm_hist_dataset_return = pandas.read_csv("ref_data/synth_test_one_rain.csv",
    #                                          usecols=['dt', 'temp', 'humidity', 'dew_point', 'wind', 'weather_id',
    #                                                   'rain_mm'])
    return owm_hist_dataset_return


# duration in minutes converted in to days, hours
def hoursindays(duration):
    days = duration / 24
    hours = duration - (24*days)

    return days, hours



# Tests


# just for testing
# lat = str(48.07)
# lon = str(11.54)

    # demo lat long isar trails
    # lat = str(48.07)
    # lon = str(11.54)


# remove after testing
def test(lat, lng):
    rain_status = 1
    time_since_rain_days = 3
    time_since_rain_hours = 0
    lastrain_duration = 1
    lastrain_intensity = 0.5
    rain_commulated_l5days = 5
    temp_avrg_l5days = 10
    wind_avrg_l5days = 0
    hum_avrg_l5days = 55
    cors_road = "dry"
    cors_gravel = "dry"
    cors_trail = "dry"

    cos_feedback = calc_cos(rain_status, time_since_rain_days, time_since_rain_hours, lastrain_intensity,
                            rain_commulated_l5days, temp_avrg_l5days, wind_avrg_l5days, hum_avrg_l5days)

    return {'rain_status': str(rain_status), 'time_since_rain_days': str(time_since_rain_days),
            'time_since_rain_hours': str(time_since_rain_hours), 'lastrain_duration_h': str(lastrain_duration),
            'lastrain_intensity_mm': str(lastrain_intensity), 'rain_commulated_l5days_mm': str(rain_commulated_l5days),
            'cos_road': cos_feedback["road"], 'cos_gravel': cos_feedback["gravel"],
            'cos_trail': cos_feedback["trail"], 'lat': str(lat), 'lng': str(lng)}

# abbriviations
# ts - timestamp