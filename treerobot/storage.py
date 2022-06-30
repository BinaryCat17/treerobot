from datetime import datetime
import math
import numpy as np


class Storage:
    time = 0
    speed = 1
    angle = 2
    x = 3
    y = 4

    @staticmethod
    def latLongToXY(refLatLong, curLatLong):
        latMid = (refLatLong[0]+curLatLong[0])/2.0
        m_per_deg_lat = 111132.954 - 559.822 * \
            math.cos(2.0 * latMid) + 1.175 * math.cos(4.0 * latMid)
        m_per_deg_lon = (3.14159265359/180) * \
            6367449 * math.cos(latMid)
        deltaLat = abs(curLatLong[0] - refLatLong[0])
        deltaLon = abs(curLatLong[1] - refLatLong[1])
        return deltaLat * m_per_deg_lat, deltaLon * m_per_deg_lon

    @staticmethod
    def parsewln(filename):
        with open(filename) as file:
            res = []

            first_lat = 0.0
            first_long = 0.0

            i = 0
            for line in file:
                if i == 3000:
                    break
                i = i + 1
                args = line.split(',')
                reg = args[0].split(';')
                time = datetime.fromtimestamp(int(reg[1]))
                lat = float(reg[2])
                long = float(reg[3])
                speed = float(reg[4])
                angle = float(reg[5])

                if first_lat == 0.0 and first_long == 0.0:
                    first_lat = lat
                    first_long = long

                x, y = Storage.latLongToXY([first_lat, first_long], [lat, long])

                res.append([
                    float((time-datetime(1970, 1, 1)).total_seconds()),
                    speed / 3.6,
                    angle,
                    x,
                    y
                ])

            data = np.array(res)
            return data

    @staticmethod
    def stdDev(d, i):
        d = d[:, i]
        return np.sqrt(np.var(d))

    @staticmethod
    def stdDevDif(d, i):
        d = d[:, i]
        prev = 0.0
        r = []
        for i in range(d.shape[0]):
            r.append(d[i] - prev)
            prev = d[i]

        return np.sqrt(np.var(r))
