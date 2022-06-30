from .track_map import TrackMap
from enum import IntFlag
import matplotlib.pyplot as plt
import numpy as np

class Draw(IntFlag):
    EstPos = 1
    ObsPos = 2
    ConfEllipse = 4
    DeadReckoningPos = 8

# в конструктор передаётся класс робота, подобно классу TrackRobot в фале test_robot.py
# модель робота как минимум должна иметь позицию x и y для визуализации
class Simulation:
    def __init__(self, robot, show_anim, anim_interval = 1, draw_flags = Draw(0)):
        self._robot = robot
        self._map = TrackMap(robot.Model)
        self._pause = False
        self._draw_flags = draw_flags
        self._show_anim = show_anim
        self._anim_interval = anim_interval
        self._xDR = np.zeros(robot.Model.xsize)
        self._run = True
        self._h_u = []
        self._h_z = []
        self._h_xEst = []
        self._h_xDR = []

    def run(self):
        anim_cnt = 0
        while self._run:
            anim_cnt = anim_cnt + 1
            # если робот закончил своё выполнение, то обновляем картинку последний раз и ставим симуляцию на паузу
            if not self._robot.enabled():
                if not self._show_anim:
                    self._map.draw()
                self._show_anim = True
                self._pause = True
            else:
                # робот может сам контролировать паузу, либо
                paused = self._robot.paused()
                # пауза может управляться рпиложением
                if paused is not None:
                    self._pause = paused

            if not self._pause:
                # считываем время, прошедшее между симуляцией dt
                # вектор управления и наблюдения, полученный от робота u, z
                # оценённый вектор состояния xEst
                # ковариационная матрица состояния P
                dt, u, z, xEst, PEst = self._robot.estimate()
                self._h_u.append(u)
                self._h_z.append(z)
                self._h_xEst.append(xEst)

                if Draw.EstPos & self._draw_flags:
                    self._map.pos_est(xEst)

                if Draw.ObsPos & self._draw_flags:
                    self._map.pos_obs(z)

                # Записываем в историю траекторию движения без учета обратной связи
                self._xDR = self._robot.Model.motion(dt, self._xDR, u)
                self._h_xDR.append(np.array([self._xDR]).T)

                if Draw.DeadReckoningPos & self._draw_flags:
                    self._map.pos_dr(self._xDR)

                if Draw.ConfEllipse & self._draw_flags:
                    self._map.conf_ellipse(PEst)

                # отрисовываем каждый n-й кадр
                if self._show_anim:
                    if anim_cnt % self._anim_interval == 0:
                        self._map.draw()

            if self._show_anim:
                plt.gcf().canvas.mpl_connect('key_release_event',
                                             lambda event: self._scan_event(event))
                plt.pause(0.001)
        
        self._robot.stop()
        self._h_u = np.array(self._h_u)
        self._h_z = np.array(self._h_z)
        self._h_xEst = np.array(self._h_xEst)
        self._h_xDR = np.array(self._h_xDR)
    
    def u_history(self):
        return self._h_u

    def z_history(self):
        return self._h_z
    
    def xEst_history(self):
        return self._h_xEst

    def xDR_history(self):
        return self._h_xDR

    def _scan_event(self, event):
        if event.key == 'escape' or event.key == 'q':
            self._run = False
        if event.key == 'enter' or event.key == 'e':
            self._pause = not self._pause
