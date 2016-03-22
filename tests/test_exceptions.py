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
from jnpr.junos.exception import CommitError
from jnpr.junos.utils.config import Config
from lxml import etree
import pytest


# ------------------------------------------------------------------------------
# test functions
# ------------------------------------------------------------------------------

def test_commit_error(device):
    """test commit error with dynamic reply"""

    # bind configuration util
    assert device.bind(cu=Config) == None

    # create error xml
    error = etree.fromstring("""
        <rpc-error xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:junos="http://xml.juniper.net/junos/14.1R4/junos" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
            <error-type>application</error-type>
            <error-tag>invalid-value</error-tag>
            <error-severity>error</error-severity>
            <error-path>[edit]</error-path>
            <error-message>mgd: Missing mandatory statement: 'test error'</error-message>
            <error-info>
                <bad-element>system</bad-element>
            </error-info>
        </rpc-error>
    """)

    # set CommitError exception as result for rpc commit_configuration
    rpc_reply_dict['commit-configuration'] = CommitError(error)

    # check if CommitError will be raised
    with pytest.raises(CommitError):
        # commit configuration
        device.cu.commit()
