#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

try:
    import numpy as np
except ImportError as e:
    print("Failed to do 'from scipy.interpolate import interp1d', "
          "scipy may not been installed properly: %s" % e)
try:
    from scipy.interpolate import interp1d
except ImportError as e:
    print("Failed to do 'from scipy.interpolate import interp1d', "
          "scipy may not been installed properly: %s" % e)

from numpymate.packages.convert2 import any2datetime
from numpymate.packages.rolex import rolex


def datetime_to_utctimestamp(datetime_array):
    return [rolex.to_utctimestamp(any2datetime(dt)) for dt in datetime_array]


def locate(x1, y1, x2, y2, x3):
    """An equation solver to solve: given two points on a line and x, solve the
    y coordinate on the same line.

    Suppose p1 = (x1, y1), p2 = (x2, y2), p3 = (x3, y3) on the same line.
    given x1, y1, x2, y2, x3, find y3::

        y3 = y1 - (y1 - y2) * (x1 - x3) / (x1 - x3)

    **中文文档**

    给定两点, 求得由这两点确定的直线上的另外一点的y坐标。
    """
    return y1 - 1.0 * (y1 - y2) * (x1 - x3) / (x1 - x2)


def datetime_mode_decorator(func):
    """

    **中文文档**
    """
    def wrapper(*args, **kwargs):
        x_axis = kwargs.get("x_axis", args[0])
        y_axis = kwargs.get("y_axis", args[1])
        x_new_axis = kwargs.get("x_new_axis", args[2])

        x_axis = datetime_to_utctimestamp(x_axis)
        x_new_axis = datetime_to_utctimestamp(x_new_axis)

        new_args = (x_axis, y_axis, x_new_axis)
        return func(*new_args)

    return wrapper


def linear_interp(x_axis, y_axis, x_new_axis):
    """Interpolate y_axis = f(x_axis) -> y_new_axis = f(x_new_axis), use 
    linear interpolation. x_new_axis's range has to be included in x_axis.

    **中文文档**

    对 y = f(x) 进行线性插值, 要求被差值的点在 x[0] ~ x[-1] 之间。
    """
    f = interp1d(x_axis, y_axis)
    return f(x_new_axis)

linear_interp_by_datetime = datetime_mode_decorator(linear_interp)


def easy_linear_interp(x_axis, y_axis, x_new_axis):
    """Interpolate y_axis = f(x_axis) -> y_new_axis = f(x_new_axis), use 
    linear interpolation. x_new_axis's range DOESN'T has to be included in x_axis.

    A smart way to interpolate arbitrary-range x_new_axis. The trick is 
    to add one more point to the original x_axis at x_new_axis[0] and 
    x_new_axis[-1], if x_new_axis is out of range.

    **中文文档**

    对 y = f(x) 进行线性插值, 不要求被差值的点在 x[0] ~ x[-1] 之间。
    """
    # 由于之后要进行列表的拼接, 所以需要将数据转化为list
    if not isinstance(x_axis, list):
        x_axis = list(x_axis)
    
    if not isinstance(y_axis, list):
        y_axis = list(y_axis)
    
    if not isinstance(x_new_axis, list):
        x_new_axis = list(x_new_axis)
    
    left_pad_x, left_pad_y = list(), list()
    right_pad_x, right_pad_y = list(), list()
    
    if x_new_axis[0] < x_axis[0]:
        left_pad_x.append(x_new_axis[0])
        left_pad_y.append(locate(x_axis[0], y_axis[0],
                                 x_axis[1], y_axis[1], x_new_axis[0]))

    if x_new_axis[-1] > x_axis[-1]:
        right_pad_x.append(x_new_axis[-1])
        right_pad_y.append(locate(x_axis[-1], y_axis[-1],
                                  x_axis[-2], y_axis[-2], x_new_axis[-1]))

    if not ((len(left_pad_x) == 0) and (len(right_pad_x) == 0)):
        x_axis = left_pad_x + x_axis + right_pad_x
        y_axis = left_pad_y + y_axis + right_pad_y

    return linear_interp(x_axis, y_axis, x_new_axis)

easy_linear_interp_by_datetime = datetime_mode_decorator(easy_linear_interp)


def spline_interp(x_axis, y_axis, x_new_axis):
    """Interpolate y_axis = f(x_axis) -> y_new_axis = f(x_new_axis), use 
    linear interpolation. x_new_axis's range has to be included in x_axis.

    `Spline interpolation <https://en.wikipedia.org/wiki/Spline_interpolation>`_
    is a popular interpolation method. Way more accurate than linear interpolate
    in average.

    **中文文档**

    对 y = f(x) 进行曲线插值, 精度较高, 计算量较大, 
    要求被差值的点在 x[0] ~ x[-1] 之间。
    """
    f = interp1d(x_axis, y_axis, kind="cubic")
    return f(x_new_axis)

spline_interp_by_datetime = datetime_mode_decorator(spline_interp)


def exam_reliability(x_axis, x_axis_new, reliable_distance, precision=0.000001):
    """When we do linear interpolation on x_axis and derive value for 
    x_axis_new, we also evaluate how can we trust those interpolated 
    data points. This is how it works:

    For each new x_axis point in x_axis new, let's say xi. Find the closest 
    point in x_axis, suppose the distance is #dist. Compare this to 
    #reliable_distance. If #dist < #reliable_distance, then we can trust it, 
    otherwise, we can't.

    The precision is to handle decimal value's precision problem. Because 
    1.0 may actually is 1.00000000001 or 0.999999999999 in computer system. 
    So we define that: if ``dist`` + ``precision`` <= ``reliable_distance``, then we 
    can trust it, else, we can't.

    Here is an O(n) algorithm implementation. A lots of improvement than 
    classic binary search one, which is O(n^2).

    :params reliable_distance: reliab distance in seconds.
    
    **中文文档**
    
    reliability检查是指: 在我们用 x, y 的原始数据, 对x_new进行差值时, 有时我们
    需要做如下判断, 如果新的差值点, 距离原始数据中最近的点的距离, 不超过某个
    设定值 ``reliable_distance`` 时, 即可视为该差值是可信赖的。
    """
    x_axis = x_axis[::-1]
    x_axis.append(-2**32)

    distance_to_closest_point = list()
    for t in x_axis_new:
        while 1:
            try:
                x = x_axis.pop()
                if x <= t:
                    left = x
                else:
                    right = x
                    x_axis.append(right)
                    x_axis.append(left)
                    left_dist, right_dist = (t - left), (right - t)
                    if left_dist <= right_dist:
                        distance_to_closest_point.append(left_dist)
                    else:
                        distance_to_closest_point.append(right_dist)
                    break
            except:
                distance_to_closest_point.append(t - left)
                break

    reliable_flag = list()
    for dist in distance_to_closest_point:
        if dist - precision - reliable_distance <= 0:
            reliable_flag.append(True)
        else:
            reliable_flag.append(False)

    return reliable_flag


def exam_reliability_by_datetime(
        datetime_axis, datetime_new_axis, reliable_distance):
    """A datetime-version that takes datetime object list as x_axis
    reliable_distance equals to the time difference in seconds.

    :params reliable_distance: reliab distance in seconds.
    
    **中文文档**
    
    根据两个时间轴进行 reliability 检查。
    """
    numeric_datetime_axis = [
        rolex.to_utctimestamp(any2datetime(dt)) for dt in datetime_axis
    ]

    numeric_datetime_new_axis = [
        rolex.to_utctimestamp(any2datetime(dt)) for dt in datetime_new_axis
    ]

    return exam_reliability(
        numeric_datetime_axis, numeric_datetime_new_axis,
        reliable_distance, precision=0.0,
    )