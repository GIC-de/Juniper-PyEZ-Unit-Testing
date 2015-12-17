"""PyEZ Device Mock

:Author:  Christian Giese
:Contact: cgiese@juniper.net

:Date:    12/17/2015
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

@pytest.fixture(scope="module")
def rpc_replys():
    """Dynamic Generated rpc-replys"""
    return {}


@patch('ncclient.manager.connect')
@pytest.fixture(scope="module")
def mocked_device(mock_connect, rpc_replys):
    """Juniper PyEZ Device Fixture"""
    def mock_manager(*args, **kwargs):
        if 'device_params' in kwargs:
            # open connection
            device_params = kwargs['device_params']
            device_handler = make_device_handler(device_params)
            session = SSHSession(device_handler)
            return Manager(session, device_handler)
        elif args:
            # rpc request
            rpc_request = args[0].tag
            if rpc_request in rpc_replys:
                xml = rpc_replys[rpc_request]
            else:
                fname = os.path.join(os.path.dirname(__file__), 'rpc-reply', rpc_request + '.xml')
                with open(fname, 'r') as f:
                    xml = f.read()
            rpc_reply = NCElement(xml, dev._conn._device_handler.transform_reply())
            return rpc_reply
    mock_connect.side_effect = mock_manager
    dev = Device(host='1.1.1.1', user='juniper', gather_facts=False)
    dev.open()
    dev._conn.rpc = MagicMock(side_effect=mock_manager)
    return dev
