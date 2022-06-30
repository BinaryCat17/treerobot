from cmath import atan
import math
import numpy as np

def normalized(a):
    return a / np.linalg.norm(a)

def rowAngle(p1, p2, forwardAngle):
    M = np.array(p2) - np.array(p1)
    Md = normalized(M) - np.array([math.cos(np.deg2rad(forwardAngle)), math.sin(np.deg2rad(forwardAngle))])
    Dd = np.sign(p1[0] * Md[1]) * abs(atan(Md[1]/ Md[0]))
    return  np.rad2deg(Dd)

print(rowAngle([448, -1000], [124, -260], 100))

vec1 = normalized(np.array([-740, -200]))
vec2 = normalized(np.array([401, -880]))
vec3 = normalized(np.array([1, 0]))
vec4 = normalized(np.array([-1, 0]))
print(np.rad2deg(np.arccos(np.dot(vec1, vec2))))
74.87