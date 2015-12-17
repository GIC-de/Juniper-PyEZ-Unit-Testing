#!/usr/bin/env python
"""Routing Neighbors

Small script using Juniper PyEZ to display all routing neighbors.

:Author:  Christian Giese
:Contact: cgiese@juniper.net

:Date:    12/17/2015
:Version: 0.1
"""
from __future__ import unicode_literals
from __future__ import print_function
from jnpr.junos import Device
from jnpr.junos.utils.util import Util

from jnpr.junos.op.lldp import LLDPNeighborTable
from jnpr.junos.op.isis import IsisAdjacencyTable
from jnpr.junos.op.ospf import OspfNeighborTable

from collections import defaultdict
import argparse


# ==============================================================================
# Classes and Functions
# ==============================================================================

class Neighbors(Util):
    """Junos Neighbor Class

    :param dev: connected device
    :type dev: jnpr.junos.Device

    :reises: jnpr.junos.exception
    """

    @property
    def lldp(self):
        if not hasattr(self, '_lldp'):
            self._lldp = LLDPNeighborTable(self.dev)
        return self._lldp.get()

    @property
    def isis(self):
        if not hasattr(self, '_isis'):
            self._isis = IsisAdjacencyTable(self.dev)
        return self._isis.get()

    @property
    def ospf(self):
        if not hasattr(self, '_ospf'):
            self._ospf = OspfNeighborTable(self.dev)
        return self._ospf.get()

    def all(self):
        """Return ALL Neighbors with protocols

        :return: dict of neighbors with IFD as key
        :rtype: dict
        """
        neighbors = defaultdict(lambda: {'protocols': set()})
        for lldp in self.lldp:
            neighbors[lldp.local_int]['hostname'] = lldp.remote_sysname
            neighbors[lldp.local_int]['protocols'].add('lldp')
        for isis in self.isis:
            ifd, unit = isis.interface_name.split('.')
            if 'hostname' not in neighbors[ifd]:
                neighbors[ifd]['hostname'] = isis.system_name
            neighbors[ifd]['protocols'].add('isis')
        for ospf in self.ospf:
            ifd, unit = ospf.interface_name.split('.')
            neighbors[ifd]['protocols'].add('ospf')
        return neighbors

    def display(self):
        """Display ALL Neighbors"""
        print("Neighbors:")
        print("%-16s %-16s %s" % ('Interface', 'Hostname', 'Protocols'))
        for ifd, attributes in self.all().iteritems():
            print("%-16s %-16s %s" % (ifd, attributes['hostname'],
                  ", ".join(attributes['protocols'])))


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Routing Neighbors\nSmall script using Juniper PyEZ to display all routing neighbors.",
        epilog='Author: cgiese@juniper.net')
    parser.add_argument(
        '--host', dest='host', action='store',
        help='host to connect',
        required=True)
    parser.add_argument(
        '--user', dest='user', action='store',
        help='username',
        required=True)
    parser.add_argument(
        '--password', dest='password', action='store',
        help='password',
        required=True)
    parameter = parser.parse_args()

    with Device(host=parameter.host, user=parameter.user, passwd=parameter.password, port=22) as dev:
        dev.bind(neighbors=Neighbors)
        dev.neighbors.display()
