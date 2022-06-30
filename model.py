import math
import numpy as np

# реализует модель робота, подобно treerobot/test_model.py
# модель подробно описана в том же файле

class Model:
    xposx = 0
    xposy = 1
    xangle = 2
    xspeed = 3
    xsize = 4

    uspeed = 0
    uangle = 1
    usize = 2

    zposx = 0
    zposy = 1
    zsize = 2

    @staticmethod
    def motion(dt, x, u):
        angle = np.deg2rad(u[Model.uangle])
        xEst = [0] * Model.xsize

        xEst[Model.xposx] = x[Model.xposx] + \
            u[Model.uspeed] * dt * math.cos(angle)

        xEst[Model.xposy] = x[Model.xposy] + \
            u[Model.uspeed] * dt * math.sin(angle)

        xEst[Model.xangle] = u[Model.uangle]
        xEst[Model.xspeed] = u[Model.uspeed]

        return xEst

    @staticmethod
    def observation(x):
        z = [0] * Model.zsize
        z[Model.zposx] = x[Model.xposx]
        z[Model.zposy] = x[Model.xposy]
        return z

