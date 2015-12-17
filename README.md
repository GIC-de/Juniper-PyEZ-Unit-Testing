[![Build Status](https://travis-ci.org/GIC-de/Juniper-PyEZ-Unit-Testing.svg)](https://travis-ci.org/GIC-de/Juniper-PyEZ-Unit-Testing)
# Juniper PyEZ Unit Testing Example
How to [unit test](https://en.wikipedia.org/wiki/Unit_testing)
your [Juniper PyEZ](https://github.com/Juniper/py-junos-eznc)
project with [pytest](https://pytest.org).

__Unit Testing does not replace functional testing__, however, it does help to
improve code quality and reduce time required to access real environments.
Unit testing enables you to test code paths that are difficult to reproduce
with a real environment, such as exception handling, and prevent regression bugs.


This example is based on the python test framework __pytest__ and __travis__
 as continuous integration (CI) service.

For this example, there is a small pyez utility called `routing_neighbors.py`
with corresponding unit tests in the directory `tests`.

You execute the tests with the command:
`python -m pytest -v --durations=10 --cov="routing_neighbors"`
as shown in `.travis.yml`.

__pytest__ auto discovery checks for all files in directory tests starting with
`tests_` and executes all included functions beginning with the same prefix.

### Mock PyEZ Device and RPC Reply

The following [pytest fixtures](https://pytest.org/latest/fixture.html) are
[mock objects](https://en.wikipedia.org/wiki/Mock_object) for your PyEZ device
connection which allow you to test your PyEZ application against an emulated
environment.

This mock object uses the root element tag of the rpc-request to return the
corresponding rpc-reply stored in the `rpc_reply_dict` or as a file in the
`directory rpc-reply`.


For the following rpc-request:
```
<get-route-information>
    <detail/>
</get-route-information>
```
This mock object attempts to retrieve the rpc-reply from the rpc_reply_dict
using `get-route-information` as the key; otherwise, it attempts to retrieve
the reply from the file `rpc-reply/get-route-information.xml`.

You must format the rpc-reply as a string similar to the following:
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

The rpc_reply_dict dict allows you to generate a rpc-reply dynamically during
test execution, such as during test combinations of outputs.
It is shown in the test function
`test_isis_dynamic` (file: `tests/test_routing_neighbors.py`).


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
def rpc_reply_dict():
    """Dynamic Generated rpc-replys"""
    return {}


@patch('ncclient.manager.connect')
@pytest.fixture(scope="module")
def mocked_device(mock_connect, rpc_reply_dict):
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
            if rpc_request in rpc_reply_dict:
                xml = rpc_reply_dict[rpc_request]
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

Within the test scripts, you then just import  `rpc_reply_dict` and
`mocked_device` from `pyez_mock`.


__Example__
```Python
from pyez_mock import mocked_device, rpc_reply_dict

def test_default(mocked_device, rpc_reply_dict):
    dev = mocked_device
    result = dev.rpc.get_route_information(detail=True)
    assert result.findtext(".//destination-count") == "5"
```
