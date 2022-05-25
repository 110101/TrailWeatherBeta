import run_algo
import M_owm_api as owm_api
import pandas
import os

def test():
    # isar trails
    lat = str(48.07)
    lng = str(11.54)
    stype = "gravel"


    # get current timestamp in UNIX
    timestamp = owm_api.time_now_UNIX()

    # load owm test data
    # django localhost test:
    # filepath = "../website/algo/ref_data/synth_test_one_rain.csv"
    # weather_data_owm = pandas.read_csv(filepath, usecols=['dt', 'temp', 'humidity', 'dew_point', 'wind', 'weather_id',
    #                                                       'rain_mm'])
    # local:
    script_dir = os.getcwd()
    filepath = "website/ref_data/synth_test_one_rain.csv"
    weather_data_owm = pandas.read_csv(os.path.normcase(os.path.join(script_dir, filepath)),
                                       usecols=['dt', 'temp', 'humidity', 'dew_point', 'wind', 'weather_id',
                                                'rain_mm'])

    # run the algo
    surface_condition = run_algo.run_algo_smplfd(weather_data_owm, lat, lng, stype)

    return surface_condition

res = test()
print(res)