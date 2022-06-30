from treerobot import UnscentedKalmanFilter
from model import Model
from receiver import Receiver
import numpy as np
import datetime

# реализует управление роботом, подобно treerobot/test_robot.py
# робот на примере подробно описан в том же файле


class GalileoRobot:
    Model = Model

    def __init__(self):
        self._filter = UnscentedKalmanFilter(GalileoRobot.Model)
        self._updated = False
        self._receiver = Receiver()
        self._last_updated_time = datetime.datetime.now()

    def enabled(self):
        return True

    def paused(self):
        return not self._updated
    
    def stop(self):
        self._receiver.stop()

    def estimate(self):
        if not self.enabled():
            return

        self._updated, self._posx, self._posy, self._speed, self._angle = self._receiver.update()

        if self._updated:
            dt = self._last_updated_time - datetime.datetime.now()
            self._last_updated_time = datetime.datetime.now()

            u, x_deviation = self._controlInput()
            self._filter.predict(dt, u, np.diag(x_deviation) ** 2)

            z, z_deviation = self._observeGNSS()
            xEst, PEst = self._filter.update(z, np.diag(z_deviation) ** 2)

            return dt, u, z, xEst, PEst
        else:
            return None
        
    def _controlInput(self):
        u = [0] * GalileoRobot.Model.usize
        u[GalileoRobot.Model.uspeed] = self._speed
        u[GalileoRobot.Model.uangle] = self._angle

        x_deviation = [0] * Model.xsize
        x_deviation[Model.xposx] = 0.93
        x_deviation[Model.xposy] = 2.04
        x_deviation[Model.xangle] = 2.862387
        x_deviation[Model.xspeed] = 0.5527557

        return u, x_deviation

    def _observeGNSS(self):
        z = [0] * GalileoRobot.Model.zsize
        z[GalileoRobot.Model.zposx] = self._posx
        z[GalileoRobot.Model.zposy] = self._posy

        z_deviation = [0] * Model.zsize
        z_deviation[Model.zposx] = 3
        z_deviation[Model.zposy] = 3

        return z, z_deviation
