import numpy as np
import math
from scipy.spatial.transform import Rotation as Rot
import matplotlib.pyplot as plt


def rot_mat_2d(angle):
    return Rot.from_euler('z', angle).as_matrix()[0:2, 0:2]


class TrackMap:
    def __init__(self, model):
        self._model = model
        self._hxEst = np.zeros((2, 0))
        self._hxDR = np.zeros((2, 0))
        self._hz = np.zeros((2, 0))
        self._PEst = None

    # записываем историю оценённых позиций робота
    def pos_est(self, xEst):
        xEst = np.array([xEst[self._model.xposx], xEst[self._model.xposy]])
        self._xEst = xEst
        self._hxEst = np.hstack([self._hxEst, xEst])

    # записываем историю позиций без учёта обратной связи
    def pos_dr(self, xDR):
        xDR = np.array([[xDR[self._model.xposx]], [xDR[self._model.xposy]]])
        self._hxDR = np.hstack([self._hxDR, xDR])

    # записываем позиции, полученную с датчиков напрямую
    def pos_obs(self, z):
        z = np.array([[z[self._model.zposx]], [z[self._model.zposy]]])
        self._hz = np.hstack([self._hz, z])

    # записываем последнюю ковариационную матрицу состояния,
    # необходимую для отрисовки области доверия
    def conf_ellipse(self, PEst):
        self._PEst = PEst

    def draw(self):
        # если в истории есть значения, то визуализируем
        plt.cla()

        if np.any(self._hz):
            plt.plot(self._hz[0, :], self._hz[1, :], ".g")

        if np.any(self._hxDR):
            plt.plot(np.array(self._hxDR[0, :]).flatten(),
                     np.array(self._hxDR[1, :]).flatten(), "-b")

        if np.any(self._hxEst):
            plt.plot(np.array(self._hxEst[0, :]).flatten(),
                     np.array(self._hxEst[1, :]).flatten(), "-r")
            if self._PEst is not None:
                self._plot_covariance_ellipse(self._xEst, self._PEst)

        plt.axis("equal")
        plt.grid(True)

    def _plot_covariance_ellipse(self, xEst, PEst):  # pragma: no cover
        eigval, eigvec = np.linalg.eig(PEst)

        if eigval[0] >= eigval[1]:
            bigind = 0
            smallind = 1
        else:
            bigind = 1
            smallind = 0

        t = np.arange(0, 2 * math.pi + 0.1, 0.1)
        a = math.sqrt(eigval[bigind])
        b = math.sqrt(eigval[smallind])
        x = [a * math.cos(it) for it in t]
        y = [b * math.sin(it) for it in t]
        angle = math.atan2(eigvec[1, bigind], eigvec[0, bigind])
        fx = rot_mat_2d(angle) @ np.array([x, y])
        px = np.array(fx[0, :] + xEst[0, 0]).flatten()
        py = np.array(fx[1, :] + xEst[1, 0]).flatten()
        plt.plot(px, py, "--r")
