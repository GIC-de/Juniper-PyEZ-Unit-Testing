"""Test PyEZ Example Module

:Organization:  Juniper Networks
:Copyright:     Juniper Networks

:Author:  Christian Giese
:Contact: cgiese@juniper.net

:Date:    12/07/2015
:Version: 0.1
"""
from __future__ import unicode_literals
from mock import MagicMock, patch
from jnpr.junos import Device
from ncclient.manager import Manager, make_device_handler
from ncclient.transport import SSHSession
from ncclient.xml_ import NCElement
import pytest
import os


# ------------------------------------------------------------------------------
# pytest fixtures
# ------------------------------------------------------------------------------

@patch('ncclient.manager.connect')
@pytest.fixture(scope="module")
def mocked_device(mock_connect):
    """Juniper PyEZ Device Fixture"""
    def mock_manager(*args, **kwargs):
        if kwargs:
            device_params = kwargs['device_params']
            device_handler = make_device_handler(device_params)
            session = SSHSession(device_handler)
            return Manager(session, device_handler)
        elif args:
            fname = args[0].tag + '.xml'
            fpath = os.path.join(os.path.dirname(__file__), 'rpc-reply', fname)
            with open(fpath, 'r') as f:
                xml = f.read()
            rpc_reply = NCElement(
                xml, dev._conn._device_handler.transform_reply())
            return rpc_reply
    mock_connect.side_effect = mock_manager
    dev = Device(host='1.1.1.1', user='juniper', gather_facts=False)
    dev.open()
    dev._conn.rpc = MagicMock(side_effect=mock_manager)
    return dev


# ------------------------------------------------------------------------------
# test functions
# ------------------------------------------------------------------------------

def test_example(mocked_device):
    dev = mocked_device
    result = dev.rpc.get_route_information(detail=True)
    assert result.findtext(".//destination-count") == "5"
