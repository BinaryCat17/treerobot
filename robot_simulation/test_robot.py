from .storage import Storage
from .test_model import Model
from .unscented_kalman_filter import UnscentedKalmanFilter
import numpy as np


class TrackRobot:
    Model = Model

    def __init__(self, data):
        self._filter = UnscentedKalmanFilter(TrackRobot.Model)
        self._data = data
        self._row = 0

    def enabled(self):
        # симуляция должна завершить выполнение, когда все данные закончатся
        return self._row + 1 < len(self._data)

    def stop(self):
        pass
    
    def paused(self):
        # виртуальный робот можно произвольно ставить на паузу
        return None

    def estimate(self):
        if not self.enabled():
            return

        dt = self._update()

        u, x_deviation = self._controlInput()

        # шаг предсказания. преобразуем стандартные отклонения в матрицу ковариации
        self._filter.predict(dt, u, np.diag(x_deviation) ** 2)

        # шаг обновления. преобразуем стандартные отклонения в матрицу ковариации
        z, z_deviation = self._observeGNSS()
        xEst, PEst = self._filter.update(z, np.diag(z_deviation) ** 2)

        return dt, u, z, xEst, PEst

    def _update(self):
        # считываем следующую строку данных
        self._row = self._row + 1

        if self._row > 0:
            return self._data[self._row][Storage.time] - self._data[self._row - 1][Storage.time]
        else:
            return 0.0

    def _controlInput(self):
        # возвращаем вектор управления
        u = [0] * TrackRobot.Model.usize
        u[TrackRobot.Model.uspeed] = self._data[self._row][Storage.speed]
        u[TrackRobot.Model.uangle] = self._data[self._row][Storage.angle] + 99.37

        # Стандартные отклонения истинных параметров робота
        # Режим передвижения может изменяться в реальном времени
        x_deviation = [0] * Model.xsize
        x_deviation[Model.xposx] = 0.93
        x_deviation[Model.xposy] = 2.04
        x_deviation[Model.xangle] = 25.862387
        x_deviation[Model.xspeed] = 0.5527557

        return u, x_deviation

    def _observeGNSS(self):
        # возвращаем вектор наблюдения
        z = [0] * TrackRobot.Model.zsize
        z[TrackRobot.Model.zposx] = self._data[self._row][Storage.x]
        z[TrackRobot.Model.zposy] = self._data[self._row][Storage.y]

        # Стандартные отклонения фактических параметров с датчиков
        # Способ измерения может изменяться в реальном времени
        z_deviation = [0] * Model.zsize
        z_deviation[Model.zposx] = 3
        z_deviation[Model.zposy] = 3

        return z, z_deviation
