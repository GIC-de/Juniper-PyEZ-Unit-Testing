"""Test PyEZ Routing Neighbors Module

:Author:  Christian Giese
:Contact: cgiese@juniper.net

:Date:    03/22/2015
:Version: 0.3
"""
from __future__ import print_function
from __future__ import unicode_literals
from pyez_mock.device import pytest_device as device
from pyez_mock.device import rpc_reply_dict
from routing_neighbors import Neighbors
from lxml import etree
from jnpr.junos import jxml as JXML
import os


# ------------------------------------------------------------------------------
# test functions
# ------------------------------------------------------------------------------

def test_open_device(device):
    """open device"""
    device.open()


def test_bind_to_pyez_dev(device):
    """bind instance of neighbors to device """
    device.bind(neighbors=Neighbors)
    assert device.neighbors.display


def test_isis(device):
    """isis adjacencys"""
    # get isis adjacencys and check if number is 3
    isis = device.neighbors.isis
    assert len(isis) == 3


def test_isis_dynamic(device):
    """isis with dynamic reply"""
    # read rpc-reply from file
    rpc_request = 'get-isis-adjacency-information'
    fname = os.path.join(os.path.dirname(__file__), 'rpc-reply', rpc_request + '.xml')
    with open(fname, 'r') as f:
        xml = etree.fromstring(f.read())
        xml = JXML.remove_namespaces(xml)
    # updated rpc-reply (delete first adjacency)
    xml.find('.//isis-adjacency-information').remove(xml.find('.//isis-adjacency'))
    # store in rpc_reply_dict dict (fixture)
    rpc_reply_dict[rpc_request] = etree.tostring(xml)
    # get isis adjacencys and check if number has decreased from 3 to 2
    isis = device.neighbors.isis
    assert len(isis) == 2
