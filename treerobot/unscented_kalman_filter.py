import scipy.linalg
import numpy as np
import math

#  UKF Parameter
ALPHA = 0.001
BETA = 2
KAPPA = 0


def generate_sigma_points(xEst, PEst, gamma):
    sigma = xEst
    Psqrt = scipy.linalg.sqrtm(PEst)
    n = len(xEst[:, 0])
    # Positive direction
    for i in range(n):
        sigma = np.hstack((sigma, xEst + gamma * Psqrt[:, i:i + 1]))

    # Negative direction
    for i in range(n):
        sigma = np.hstack((sigma, xEst - gamma * Psqrt[:, i:i + 1]))

    return sigma


def predict_sigma_motion(dt, sigma, u, motion_model):
    for i in range(sigma.shape[1]):
        sigma[:, i] = motion_model(dt, sigma[:, i], u)

    return sigma


def predict_sigma_observation(sigma, observation_model):
    for i in range(sigma.shape[1]):
        sigma[0:2, i] = observation_model(sigma[:, i])

    sigma = sigma[0:2, :]

    return sigma


def calc_sigma_covariance(x, sigma, wc, Pi):
    nSigma = sigma.shape[1]
    d = sigma - x[0:sigma.shape[0]]
    P = Pi
    for i in range(nSigma):
        P = P + wc[0, i] * d[:, i:i + 1] @ d[:, i:i + 1].T
    return P


def calc_pxz(sigma, x, z_sigma, zb, wc):
    nSigma = sigma.shape[1]
    dx = sigma - x
    dz = z_sigma - zb[0:2]
    P = np.zeros((dx.shape[0], dz.shape[0]))

    for i in range(nSigma):
        P = P + wc[0, i] * dx[:, i:i + 1] @ dz[:, i:i + 1].T

    return P


class UnscentedKalmanFilter:
    def __init__(self, robot_model):
        self._motion_model = robot_model.motion
        self._observation_model = robot_model.observation

        nx = robot_model.xsize
        self._xEst = np.zeros((nx, 1))
        self._PEst = np.eye(nx)

        lamb = ALPHA ** 2 * (nx + KAPPA) - nx
        # calculate weights
        wm = [lamb / (lamb + nx)]
        wc = [(lamb / (lamb + nx)) + (1 - ALPHA ** 2 + BETA)]

        for _ in range(2 * nx):
            wm.append(1.0 / (2 * (nx + lamb)))
            wc.append(1.0 / (2 * (nx + lamb)))

        self._gamma = math.sqrt(nx + lamb)
        self._wm = np.array([wm])
        self._wc = np.array([wc])

    # шаг предсказания позиции робота в следующий момент времени
    # dt - время с моментра прошлого предсказания
    # u - управляющий вектор
    # Q - ковариационная матрица ошибки модели
    def predict(self, dt, u, Q):
        sigma = generate_sigma_points(self._xEst, self._PEst, self._gamma)
        sigma = predict_sigma_motion(dt, sigma, u, self._motion_model)

        self._xEst = (self._wm @ sigma.T).T
        self._PEst = calc_sigma_covariance(
            self._xEst, sigma, self._wc, Q)

    # шаг обновления можно вызывать несколько раз после вызова шага предсказания
    # каждый вызов вносит корректировку для вызова predict
    # R - ковариационная матрица шума измерений
    def update(self, z, R):
        zPred = self._observation_model(self._xEst)
        y = np.array([z]).T - zPred

        sigma = generate_sigma_points(self._xEst, self._PEst, self._gamma)
        zb = (self._wm @ sigma.T).T
        z_sigma = predict_sigma_observation(sigma, self._observation_model)
        st = calc_sigma_covariance(zb, z_sigma, self._wc, R)
        Pxz = calc_pxz(sigma, self._xEst, z_sigma, zb, self._wc)
        K = Pxz @ np.linalg.inv(st)
        self._xEst = self._xEst + K @ y
        self._PEst = self._PEst - K @ st @ K.T

        # возвращаем оценённый вектор состояния и матрицу ковариации состояния
        return self._xEst, self._PEst
