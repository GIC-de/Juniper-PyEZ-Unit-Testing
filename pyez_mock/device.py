"""PyEZ Device Mock

:Author:  Christian Giese
:Contact: cgiese@juniper.net

:Date:    03/22/2016
:Version: 0.3
"""
from __future__ import unicode_literals
from mock import MagicMock, patch
from jnpr.junos import Device
from jnpr.junos.facts.swver import version_info
from ncclient.manager import Manager, make_device_handler
from ncclient.transport import SSHSession
from ncclient.xml_ import NCElement
import pytest
import os

__all__ = ["rpc_reply_dict", "device_facts", "device", "pytest_device"]

# dynamic generated rpc-replys
rpc_reply_dict = {}

# junos device facts
device_facts = {
 '2RE': True,
 'HOME': '/var/home/juniper',
 'RE0': {'last_reboot_reason': 'Router rebooted after a normal shutdown.',
         'mastership_state': 'master',
         'model': 'RE-S-1800x4',
         'status': 'OK',
         'up_time': '19 days, 16 hours, 57 minutes, 47 seconds'},
 'RE1': {'last_reboot_reason': 'Router rebooted after a normal shutdown.',
         'mastership_state': 'backup',
         'model': 'RE-S-1800x4',
         'status': 'OK',
         'up_time': '19 days, 16 hours, 58 minutes, 11 seconds'},
 'domain': 'mocked.juniper.domain',
 'fqdn': 'mx960.mocked.juniper.domain',
 'hostname': 'mx960',
 'ifd_style': 'CLASSIC',
 'master': 'RE0',
 'model': 'mx960',
 'personality': 'MX',
 'serialnumber': 'JN1337NA1337',
 'switch_style': 'BRIDGE_DOMAIN',
 'vc_capable': False,
 'version': '13.3R8',
 'version_RE0': '13.3R8',
 'version_RE1': '13.3R8',
 'version_info': version_info('13.3R8')
}


@patch('ncclient.manager.connect')
def device(mock_connect, *args, **kwargs):
    """Juniper PyEZ Device Mock"""

    def get_facts():
        dev._facts = device_facts

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
            if rpc_request == "command":
                # CLI commands
                rpc_request = "%s_%s" % (rpc_request, args[0].text.replace(" ", "_"))
            if rpc_request in rpc_reply_dict:
                # result for rpc request is in dict
                reply = rpc_reply_dict[rpc_request]
                if isinstance(reply, Exception):
                    raise reply
                else:
                    xml = reply
            else:
                # get rpc result from file
                fname = os.path.join(os.getcwd(), 'tests', 'rpc-reply', rpc_request + '.xml')
                with open(fname, 'r') as f:
                    xml = f.read()
            rpc_reply = NCElement(xml, dev._conn._device_handler.transform_reply())
            return rpc_reply

    mock_connect.side_effect = mock_manager
    dev = Device(*args, **kwargs)
    dev.facts_refresh = get_facts
    dev.open()
    dev._conn.rpc = MagicMock(side_effect=mock_manager)
    # replace open/close with mock objects
    dev.open = MagicMock()
    dev.close = MagicMock()
    return dev


# ------------------------------------------------------------------------------
# pytest fixtures
# ------------------------------------------------------------------------------

@pytest.fixture(scope="module", params=[{"host": "1.2.3.4", "user": "juniper"}])
def pytest_device(request):
    return device(**request.param)
