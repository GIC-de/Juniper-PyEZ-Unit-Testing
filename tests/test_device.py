"""Test PyEZ CLI commands

:Author:  Christian Giese
:Contact: cgiese@juniper.net

:Date:    03/22/2015
:Version: 0.3
"""
from __future__ import print_function
from __future__ import unicode_literals
from pyez_mock.device import pytest_device as device
from pyez_mock.device import device as user_device
from pyez_mock.device import rpc_reply_dict
from pyez_mock.device import device_facts
from jnpr.junos.facts.swver import version_info
import pytest


# ------------------------------------------------------------------------------
# test functions
# ------------------------------------------------------------------------------

# The open/close methods of the device are replaced with MagicMock
# which means that the execution of these has no impact on the mocked device.

def test_open_device(device):
    """optional open pyez device"""
    # the open/c
    assert device.open()


def test_close_device(device):
    assert device.close()


# Facts are gathered from fictionary device_facts.

def test_device_facts(device):
    assert device.facts['model'] == "mx960"


def test_update_facts(device):
    new_version = {
        'version':      '14.1R1',
        'version_RE0':  '14.1R1',
        'version_RE1':  '14.1R1',
        'version_info': version_info('14.1R1')
    }
    device_facts.update(new_version)
    assert device.facts['version'] == '14.1R1'


# ------------------------------------------------------------------------------
# create and test user defined device fixture
# ------------------------------------------------------------------------------

@pytest.fixture(scope="module", params=[{"host": "5.6.7.8", "user": "test", "password": "test"}])
def user_pytest_device(request):
    return user_device(**request.param)


def test_user_device_repr(user_pytest_device):
    assert str(user_pytest_device) == "Device(5.6.7.8)"


def test_userdevice_facts(user_pytest_device):
    assert user_pytest_device.facts['model'] == "mx960"
