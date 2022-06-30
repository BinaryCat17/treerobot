from tree_robot.robot import GalileoRobot
from robot_simulation import Simulation, Draw

DRAW_FLAGS = Draw.EstPos | Draw.ObsPos | Draw.ConfEllipse | Draw.DeadReckoningPos
ENABLE_ANIMATION = True
ANIMATION_INTERVAL = 0

def run():
    robot = GalileoRobot()
    app = Simulation(robot, ENABLE_ANIMATION, ANIMATION_INTERVAL, DRAW_FLAGS)
    app.run()