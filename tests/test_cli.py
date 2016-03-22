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


# ------------------------------------------------------------------------------
# test functions
# ------------------------------------------------------------------------------

def test_cli(device):
    """test cli commands with dynamic reply"""

    rpc_reply_dict["command_show_chassis_alarms"] = """
        <rpc-reply>
            <alarm-information>
                <alarm-summary>
                    <no-active-alarms/>
                </alarm-summary>
            </alarm-information>
        </rpc-reply>"""

    result = device.cli("show chassis alarms", format="xml")
    assert result.find(".//no-active-alarms") is not None
