#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd

try:
    from convert2.packages import chardet
    from convert2.packages.rolex import rolex
    from convert2.packages.six import string_types, binary_type
    from convert2.util import extract_number_from_string
except:
    from .packages import chardet
    from .packages.rolex import rolex
    from .packages.six import string_types, binary_type
    from .util import extract_number_from_string


class Anything2Int(object):

    """Parse anything to ``int``

    The logic:

    - for int:
    - for float:
    - for str: extract int
    - for datetime: it's utc timestamp
    - for date: it's days from ordinary
    - for timedelta: its total seconds
    """
    ROUND_FLOAT_METHOD = "round"  # could be one of 'floor', 'ceiling', 'round'
    EXTRACT_NUMBER_FROM_TEXT = True

    def __call__(self, value):
        #--- None ---
        if value is None:
            return None

        try:
            if np.isnan(value):
                return None
        except:
            pass

        #--- int, long, np.int, np.int8, np.int16, np.int32, np.int64 ---
        try:
            if int(value) == value:
                return int(value)
        except:
            pass

        #--- float, np.float, np.float16, np.float32, np.float64 ---
        if type(value).__name__.startswith("float"):
            return int(round(value))

        #--- str, unicode, np.str ---
        if isinstance(value, string_types):
            # if a parsable int str, like "123"
            try:
                return int(value)
            except ValueError:
                pass

            # if a parsable float str, like "3.14"
            try:
                float_ = float(value)
                return self(float_)
            except ValueError:
                pass

            # if a extractable parsable str, like "a 3.14 b"
            if self.EXTRACT_NUMBER_FROM_TEXT:
                result = extract_number_from_string(value)
                if len(result) == 1:
                    return self(float(result[0]))
                else:
                    raise ValueError("%r is not int parsable!" % value)

        #--- datetime, np.datetime64, pd.tslib.Timestamp ---
        if isinstance(value, pd.tslib.Timestamp):
            try:
                return self((value - pd.tslib.Timestamp("1970-01-01 00:00:00Z"))
                            .total_seconds())
            except:
                raise ValueError("%r is not int parsable!" % value)

        if isinstance(value, np.datetime64):
            try:
                return self(rolex.to_utctimestamp(value.astype(datetime)))
            except:
                raise ValueError("%r is not int parsable!" % value)

        if isinstance(value, datetime):
            try:
                return self(rolex.to_utctimestamp(value))
            except:
                raise ValueError("%r is not int parsable!" % value)

        #--- date ---
        if isinstance(value, date):
            try:
                return rolex.to_ordinal(value)
            except Exception as e:
                raise ValueError("%r is not int parsable!" % value)

        #--- timedelta ---
        if isinstance(value, timedelta):
            try:
                return self(value.total_seconds())
            except Exception as e:
                raise ValueError("%r is not int parsable!" % value)

        #--- other type ---
        try:
            return int(value)
        except:
            raise ValueError("%r is not int parsable!" % value)


any2int = Anything2Int()


class Anything2Float(object):

    """Parse anything to float

    The logic:

    - for int:
    - for float:
    - for str:
    - for datetime: it's utc timestamp
    - for date: it's days from ordinary
    - for timedelta: its total seconds
    """
    EXTRACT_NUMBER_FROM_TEXT = True

    def __call__(self, value):
        #--- None ---
        if value is None:
            return None

        try:
            if np.isnan(value):
                return None
        except:
            pass

        #--- int, long, np.int, np.int8, np.int16, np.int32, np.int64 ---
        #--- float, np.float, np.float16, np.float32, np.float64 ---
        try:
            return float(value)
        except:
            pass

        #--- str, unicode, np.str ---
        if isinstance(value, string_types):
            # if a parsable float str, like "3.14"
            try:
                return float(value)
            except ValueError:
                pass

            # if a extractable parsable str, like "a 3.14 b"
            if self.EXTRACT_NUMBER_FROM_TEXT:
                result = extract_number_from_string(value)
                if len(result) == 1:
                    return float(result[0])
                else:
                    raise ValueError("%r is not float parsable!" % value)

        #--- datetime, np.datetime64, pd.tslib.Timestamp ---
        if isinstance(value, pd.tslib.Timestamp):
            try:
                return self((value - pd.tslib.Timestamp("1970-01-01 00:00:00Z"))
                            .total_seconds())
            except:
                raise ValueError("%r is not float parsable!" % value)

        if isinstance(value, np.datetime64):
            try:
                return self(rolex.to_utctimestamp(value.astype(datetime)))
            except:
                raise ValueError("%r is not float parsable!" % value)

        if isinstance(value, datetime):
            try:
                return self(rolex.to_utctimestamp(value))
            except:
                raise ValueError("%r is not float parsable!" % value)

        #--- date ---
        if isinstance(value, date):
            try:
                return float(rolex.to_ordinal(value))
            except Exception as e:
                raise ValueError("%r is not float parsable!" % value)

        #--- timedelta ---
        if isinstance(value, timedelta):
            try:
                return self(value.total_seconds())
            except Exception as e:
                raise ValueError("%r is not float parsable!" % value)

        #--- other type ---
        try:
            return int(value)
        except:
            raise ValueError("%r is not float parsable!" % value)


any2float = Anything2Float()


class Anything2Str(object):

    """Parse anything to ``str``

    The logic:

    - bytes: auto detect encoding and then decode
    - other: stringlize it
    """

    def __call__(self, value):
        #--- None ---
        if value is None:
            return None

        try:
            if np.isnan(value):
                return None
        except:
            pass

        #--- bytes ---
        if isinstance(value, binary_type):
            result = chardet.detect(value)
            return value.decode(result["encoding"])

        #--- other type ---
        try:
            return str(value)
        except:
            raise ValueError("%r is not str parsable!" % value)


any2str = Anything2Str()


class Anything2Datetime(object):

    """Parse anything to ``datetime.datetime``.

    The logic:

    - for int, it's the ``datetime.from_utctimestamp(value)``
    - for float, it's the ``datetime.from_utctimestamp(value)``
    - for str, try to parse ``datetime``
    - for datetime type, it's itself
    - for date type, it's the time at 00:00:00
    """

    def __call__(self, value):
        #--- None ---
        if value is None:
            return None

        try:
            if np.isnan(value):
                return None
        except:
            pass

        #--- int, long, np.int, np.int8, np.int16, np.int32, np.int64 ---
        try:
            if int(value) == value:
                try:
                    return rolex.from_utctimestamp(value)
                except:
                    raise ValueError("%r is not datetime parsable!" % value)
        except:
            pass

        #--- float, np.float, np.float16, np.float32, np.float64 ---
        if type(value).__name__.startswith("float"):
            try:
                return rolex.from_utctimestamp(value)
            except:
                raise ValueError("%r is not datetime parsable!" % value)

        #--- np.datetime64, pd.tslib.Timestamp ---
        if isinstance(value, pd.tslib.Timestamp):
            try:
                return value.to_pydatetime()
            except:
                raise ValueError("%r is not datetime parsable!" % value)

        if isinstance(value, np.datetime64):
            try:
                return value.astype(datetime)
            except:
                raise ValueError("%r is not datetime parsable!" % value)

        # --- other type ---
        try:
            return rolex.parse_datetime(value)
        except:
            raise ParseDatetimeError(str(e))

any2datetime = Anything2Datetime()


class Anything2Date(object):

    """Parse anything to ``datetime.date``.

    The logic:

    - for int, it's the ``datetime.fromordinal(value)``
    - for float, it's a invalid input
    - for str, try to parse ``date``
    - for datetime type, it's the date part
    - for date type, it's itself
    """

    def __call__(self, value):
        #--- None ---
        if value is None:
            return None

        try:
            if np.isnan(value):
                return None
        except:
            pass

        #--- int, long, np.int, np.int8, np.int16, np.int32, np.int64 ---
        try:
            if int(value) == value:
                try:
                    return rolex.from_ordinal(value)
                except:
                    raise ValueError("%r is not date parsable!" % value)
        except:
            pass

        #--- float, np.float, np.float16, np.float32, np.float64 ---
        if type(value).__name__.startswith("float"):
            raise ValueError("%r is not date parsable!" % value)

        #--- np.datetime64, pd.tslib.Timestamp ---
        # --- other type ---
        try:
            return any2datetime(value).date()
        except:
            raise ValueError("%r is not date parsable!" % value)

any2date = Anything2Date()
