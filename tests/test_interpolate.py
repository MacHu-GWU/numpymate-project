#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import numpy as np
from numpymate import interpolate


def test_linear_interp():
    x = [1, 2, 3]
    y = [1, 2, 3]
    x_new1 = [1, 1.5, 2, 2.5, 3]
    y_new1 = interpolate.easy_linear_interp(x, y, x_new1, enable_warning=False)
    x_new2 = [0, 1, 2, 3, 4]
    y_new2 = interpolate.easy_linear_interp(x, y, x_new2, enable_warning=False)

    for i, j in zip(y_new1, [1, 1.5, 2, 2.5, 3]):
        assert abs(i - j) <= 0.000001
    for i, j in zip(y_new2, [0, 1, 2, 3, 4]):
        assert abs(i - j) <= 0.000001


def test_linear_interp_by_datetime():
    x = np.array([
        datetime(2014, 1, 1, 0, 0, 10),
        datetime(2014, 1, 1, 0, 0, 20),
    ])
    y = [1, 2]
    x_new1 = np.array([
        datetime(2014, 1, 1, 0, 0, 5),
        datetime(2014, 1, 1, 0, 0, 15),
        datetime(2014, 1, 1, 0, 0, 25),
    ])
    y_new1 = interpolate.easy_linear_interp_by_datetime(
        x, y, x_new1, enable_warning=False)
    for i, j in zip(y_new1, [0.5, 1.5, 2.5]):
        assert abs(i - j) <= 0.000001


def test_exam_reliability():
    # dist [0.6, 0.4, 0.3, 0.5, 0.3, 0.4, 0.5]
    # flag [False, True, True, False, True, True, False]
    x = [1, 2, 3, 4]
    x_new = [0.4, 0.6, 1.7, 2.5, 3.3, 4.4, 4.5]

    reliable_flag = interpolate.exam_reliability(x, x_new, 0.4)
    reliable_flag_expect = [False, True, True, False, True, True, False]

    assert reliable_flag == reliable_flag_expect


def test_exam_reliability_by_datetime():
    # dist [25, 20, 15, 15, 20, 25, 25, 20, 15, 15, 20, 25]
    # flag [False, True, True, True, True, False, False, True, True, True, True, False]
    datetime_axis = np.array([
        datetime(2014, 1, 1, 0, 10, 0),
        datetime(2014, 1, 1, 0, 11, 0),
    ])
    datetime_new_axis = np.array([
        datetime(2014, 1, 1, 0, 9, 35),
        datetime(2014, 1, 1, 0, 9, 40),
        datetime(2014, 1, 1, 0, 9, 45),

        datetime(2014, 1, 1, 0, 10, 15),
        datetime(2014, 1, 1, 0, 10, 20),
        datetime(2014, 1, 1, 0, 10, 25),

        datetime(2014, 1, 1, 0, 10, 35),
        datetime(2014, 1, 1, 0, 10, 40),
        datetime(2014, 1, 1, 0, 10, 45),

        datetime(2014, 1, 1, 0, 11, 15),
        datetime(2014, 1, 1, 0, 11, 20),
        datetime(2014, 1, 1, 0, 11, 25),
    ])

    reliable_flag = interpolate.exam_reliability_by_datetime(
        datetime_axis, datetime_new_axis, 20)
    reliable_flag_expect = [
        False, True, True,
        True, True, False,
        False, True, True,
        True, True, False,
    ]
    assert reliable_flag == reliable_flag_expect


def compare():
    import matplotlib.pyplot as plt

    x = np.linspace(0, 10, 10)
    y = np.cos(-x**2 / 8.0)
    x_new = np.linspace(0, 10, 40)

    y_cubic = interpolate.spline_interp(x, y, x_new)
    y_linear = interpolate.linear_interp(x, y, x_new)

    plt.plot(x, y, "o",
             x_new, y_cubic, "g-",
             x_new, y_linear, "r--")
    plt.ylim([-1.05, 2.05])
    plt.legend(["raw data", "cubic interp", "linear interp"])
    plt.show()


if __name__ == "__main__":
    import py
    import os
    py.test.cmdline.main("%s --tb=native -s" % os.path.basename(__file__))

    compare()
