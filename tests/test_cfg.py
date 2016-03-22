"""Test PyEZ CLI commands

:Author:  Christian Giese
:Contact: cgiese@juniper.net

:Date:    03/22/2015
:Version: 0.3
"""
from __future__ import print_function
from __future__ import unicode_literals
from pyez_mock.device import pytest_device as device
from pyez_mock.device import rpc_reply_dict
from jnpr.junos.utils.config import Config


# ------------------------------------------------------------------------------
# test functions
# ------------------------------------------------------------------------------

def test_commit_error(device):
    """test commit error with dynamic reply"""

    # bind configuration util
    assert device.bind(cu=Config) == None

    # set result for rpc load_config
    rpc_reply_dict['load-configuration'] = """
        <rpc-reply>
            <load-configuration-results>
                <ok/>
            </load-configuration-results>
        </rpc-reply>"""

    # load confgiuratin and check result
    result = device.cu.load("set interfaces ge-0/0/0 disable", format="set")
    assert result.find(".//ok") is not None
