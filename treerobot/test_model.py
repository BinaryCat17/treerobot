import math
import numpy as np

# математическая модель робота
class Model:
    # лучше придерживаться стандартных именований элементов векторов, подбно этому файлу,
    # это позволяет реализовывать обобщенные алгоритмы. Например визуализация требует наличия
    # у модели xposx, xposy, zposx, zposy. Не имеет значения, под каким номером эти свойства
    # лежат в векторе.

    # вектор состояния - то, что оценивается фильтром Калмана
    xposx = 0
    xposy = 1
    xangle = 2
    xspeed = 3
    xsize = 4

    # вектор управления - показания с первичных датчиков, непосредственно отражающих
    # управляющее воздействие на робота
    uspeed = 0
    uangle = 1
    usize = 2

    # вектор наблюдения - данные с датчиков, здесь - данные с GNSS
    zposx = 0
    zposy = 1
    zsize = 2

    @staticmethod
    def motion(dt, x, u):
        # в идеальном мире с помощью мгновенной скорости и
        # угла поворота можно точно предсказать позицию робота
        # но на практике, она будет отколняться из-за неровностей
        # фильтр скорректирует показания модели

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
        # предсказываем показания датчиков на основании текущего вектора состояний.
        # в идеальном мире показания GNSS полностью согласуются с позицией робота.
        # в фильтре этот вектор будет сравниваться с реальными значениями датчиков

        z = [0] * Model.zsize
        z[Model.zposx] = x[Model.xposx]
        z[Model.zposy] = x[Model.xposy]
        return z
