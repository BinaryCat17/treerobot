from test_robot import TrackRobot
from simulation import Draw, Simulation
from storage import Storage
import numpy as np

DRAW_FLAGS = Draw.EstPos | Draw.ObsPos | Draw.ConfEllipse# | Draw.DeadReckoningPos
ENABLE_ANIMATION = False
ANIMATION_INTERVAL = 50


def main():
    data = Storage.parsewln("BEDNAR Swifter SE 12000.wln")
    print("Стандартные отклонения датасета:")
    print("Позиция x -",
          "{0:0.2f}м".format(Storage.stdDevDif(data, Storage.x)))
    print("Позиция y -",
          "{0:0.2f}м".format(Storage.stdDevDif(data, Storage.y)))
    print("Угол -",
          "{0:0.2f}°".format(Storage.stdDevDif(data, Storage.angle)))
    print("Скорость -",
          "{0:0.2f}м/с".format(Storage.stdDevDif(data, Storage.speed)))

    robot = TrackRobot(data)
    app = Simulation(robot, ENABLE_ANIMATION, ANIMATION_INTERVAL, DRAW_FLAGS)

    app.run()

    xEst = app.xEst_history()
    xDR = app.xDR_history()

    print("Среднеквадратическая ошибка траектории, оценнёной аналитически, от скорректированной по датчикам:",
          "{0:0.2f}м".format(np.sqrt(np.sum((xEst - xDR) ** 2))))

if __name__ == '__main__':
    main()
