[![Build Status](https://travis-ci.org/GIC-de/Juniper-PyEZ-Unit-Testing.svg)](https://travis-ci.org/GIC-de/Juniper-PyEZ-Unit-Testing)
# Juniper PyEZ Unit Testing Example
How to [unit test](https://en.wikipedia.org/wiki/Unit_testing)
your [Juniper PyEZ](https://github.com/Juniper/py-junos-eznc)
project with [pytest](https://pytest.org).

__Unit Testing is no Replacement of Functional Testing__
but it helps to improve code quality and reduces the time you need access to
real environments. Unit testing allows you to test some code paths that are
hard to reproduce with real environment (e.g. exception handling, ...) and is
a great tool to prevent regression bugs.

This tutorial is based on the python test framework __pytest__ and __travis__ as
continuous integration (CI) service.

As an example there is a small pyez utility called `routing_neighbors.py`
with corresponding unit tests in the directory `tests`.

The tests will executed by the command
`python -m pytest -v --durations=10 --cov="routing_neighbors"`
as shown in `.travis.yml`. __pytest__ auto discovery checks for all files in
directory tests starting with `tests_` and executes all included functions
starting with the same prefix.

### Mock PyEZ Device and RPC Replays

The following [pytest fixtures](https://pytest.org/latest/fixture.html) are
[mock objects](https://en.wikipedia.org/wiki/Mock_object) for your
pyez device connection.

This allows you to test your pyez application against an emulated environment.

This mock uses the root element tag of the rpc-request to return the
corresponding rpc-reply stored in the rpc_replys dict or as file in directory
rpc-reply.

For the following rpc-request ...
```
<get-route-information>
    <detail/>
</get-route-information>
```
this mock tries to get the rpc-reply from the rpc_replys dict using
`get-route-information` as key otherwise it tries to get the reply from file
`rpc-reply/get-route-information.xml`.

The rpc-reply must be a string formatted like:
```
<rpc-reply xmlns:junos="http://xml.juniper.net/junos/14.1R4/junos">
    <isis-adjacency-information xmlns="http://xml.juniper.net/junos/14.1R4/junos-routing" junos:style="brief">
        <isis-adjacency>
            <interface-name>ge-0/0/1.0</interface-name>
            <system-name>MX1</system-name>
            <level>2</level>
            <adjacency-state>Up</adjacency-state>
            <holdtime>24</holdtime>
        </isis-adjacency>
        <isis-adjacency>
            <interface-name>ge-0/0/2.0</interface-name>
            <system-name>MX2</system-name>
            <level>2</level>
            <adjacency-state>Up</adjacency-state>
            <holdtime>19</holdtime>
        </isis-adjacency>
        <isis-adjacency>
            <interface-name>ge-0/0/3.10</interface-name>
            <system-name>MX3</system-name>
            <level>1</level>
            <adjacency-state>Up</adjacency-state>
            <holdtime>24</holdtime>
        </isis-adjacency>
    </isis-adjacency-information>
    <cli>
        <banner>{master}</banner>
    </cli>
</rpc-reply>
```

The rpc_replys dict allows you to generate rpc-replys dynamically during test
execution (e.g. test combinations of outputs, ...).

#### Mock Code

__tests/pyez_mock.py__
```Python
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
```

Within the test scripts just import `rpc_reply` and `mocked_device` from `pyez_mock`.

__Example__
```Python
from pyez_mock import mocked_device, rpc_replys

def test_default(mocked_device, rpc_replys):
    dev = mocked_device
    result = dev.rpc.get_route_information(detail=True)
    assert result.findtext(".//destination-count") == "5"
```
