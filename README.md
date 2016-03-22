[![Build Status](https://travis-ci.org/GIC-de/Juniper-PyEZ-Unit-Testing.svg)](https://travis-ci.org/GIC-de/Juniper-PyEZ-Unit-Testing)
# Juniper PyEZ Unit Testing and Mocking
How to [unit test](https://en.wikipedia.org/wiki/Unit_testing)
your [Juniper PyEZ](https://github.com/Juniper/py-junos-eznc) project.

__Unit Testing does not replace functional testing__, however, it does help to
improve code quality and reduce time required to access real environments by
testing against mocked (faked) environments. Mocking is the replacement of one
or more function calls or objects with mock calls or objects.

Unit testing help to prevent regression bugs. Testing with mocked environments
enables you to test code paths that are difficult to reproduce with a real
environment, such as exception handling.

This project includes a few examples and a small pyez utility called
`routing_neighbors.py` with corresponding unit tests in the directory `tests`.

The examples are based on the python test framework __pytest__ and __travis__
as continuous integration (CI) service.

You execute the tests with the command:
`python -m pytest -v --durations=10 --cov="routing_neighbors"`
as shown in `.travis.yml`.

__pytest__ auto discovery checks for all files in directory tests starting with
`tests_` and executes all included functions beginning with the same prefix.


## Mock PyEZ Device and RPC Reply

The [mock object](https://en.wikipedia.org/wiki/Mock_object) for
your PyEZ device connection (`pyez_mock/device.py`) allow you to test your PyEZ
application against an emulated environment.

This mock object uses the root element tag of the rpc-request to return the
corresponding rpc-reply stored in the `rpc_reply_dict` or as a file in the
`directory rpc-reply`.

For the following rpc-request:

```
<get-route-information>
    <detail/>
</get-route-information>
```

The mocked PyEZ device attempts to retrieve the rpc-reply from the rpc_reply_dict
using `get-route-information` as the key; otherwise, it attempts to retrieve
the reply from the file `tests/rpc-reply/get-route-information.xml` relative to
working directory. The parameters of the rpc-request will be ignored
(e.g. <detail/>).

You must format the rpc-reply as a string with a valid XML structure and
`rpc-reply` as root element:

```
from pyez_mock.device import rpc_reply_dict

rpc_reply_dict['get-alarm-information'] = """
    <rpc-reply>
        <alarm-information>
            <alarm-summary>
                <no-active-alarms/>
            </alarm-summary>
        </alarm-information>
    </rpc-reply>"""
```

The rpc_reply_dict allows you to generate a rpc-reply dynamically during
test execution or to return exceptions (see `tests/test_exceptions.py`).

### Example

```Python
from pyez_mock.device import device

dev = device(host="1.2.3.4", user="juniper")
result = device.rpc.get_route_information(detail=True)
assert result.findtext(".//destination-count") == "5"
```

#### With PyTest

`pytest_device` is a pre-defined pytest fixture with module level scope and
default credentials. You can create custom device fixtures as shown in
`tests/test_device.py`.

```Python
from pyez_mock.device import pytest_device as device

def test_default(device):
    result = device.rpc.get_route_information(detail=True)
    assert result.findtext(".//destination-count") == "5"
```
