import csv
from datetime import datetime
from datetime import date




def writelogfile(lat, lon, surface, condition):

    # get current date and time
    timestamp = str(datetime.now())
    date = timestamp.split()[0]
    time = timestamp.split()[1].split('.')[0]

    # create file name
    filename = 'algo/dojo_data/' + str(date) + '_' + str(time) + '_trailkondico_dojo' + '_' + surface +  '_' + condition + '.csv'

    # write csv
    try:
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            row_array = [date, time, lat, lon, surface, condition]
            row = row_array
            writer.writerow(row)
    except IOError:
        print("error" + date + '_' + time)



    return
