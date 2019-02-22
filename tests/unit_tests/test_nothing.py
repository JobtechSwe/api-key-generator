#-*- coding: utf-8 -*-
import pytest
import sys


@pytest.mark.unit
def test_nothing():
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    pass
