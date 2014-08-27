# ######################################################################
# Copyright (c) 2014, Brookhaven Science Associates, Brookhaven        #
# National Laboratory. All rights reserved.                            #
#                                                                      #
# Redistribution and use in source and binary forms, with or without   #
# modification, are permitted provided that the following conditions   #
# are met:                                                             #
#                                                                      #
# * Redistributions of source code must retain the above copyright     #
#   notice, this list of conditions and the following disclaimer.      #
#                                                                      #
# * Redistributions in binary form must reproduce the above copyright  #
#   notice this list of conditions and the following disclaimer in     #
#   the documentation and/or other materials provided with the         #
#   distribution.                                                      #
#                                                                      #
# * Neither the name of the Brookhaven Science Associates, Brookhaven  #
#   National Laboratory nor the names of its contributors may be used  #
#   to endorse or promote products derived from this software without  #
#   specific prior written permission.                                 #
#                                                                      #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS  #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT    #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS    #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE       #
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,           #
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES   #
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR   #
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)   #
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,  #
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OTHERWISE) ARISING   #
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE   #
# POSSIBILITY OF SUCH DAMAGE.                                          #
########################################################################
'''
Created on Apr 29, 2014
'''
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from PyQt4 import QtCore, QtGui
from vistrails.core.modules.vistrails_module import Module, ModuleSettings
from vistrails.core.modules.config import IPort, OPort
import numpy as np
import logging
from pymongo.errors import ConnectionFailure

logger = logging.getLogger(__name__)

try:
    from metadataStore.userapi.commands import search
except (ImportError, ConnectionFailure) as e:
    def search(*args, **kwargs):
        err_msg = ("search from metadataStore.userapi.commands is not "
                   "importable. Search cannot proceed")
        print("userpackages/NSLS2/broker.py: {0}".format(err_msg))
        logger.warning(err_msg)

try:
    from metadataStore.userapi.commands import search_keys_dict
except (ImportError, ConnectionFailure) as e:
    search_keys_dict = {}
    search_keys_dict["broker_unavailable"] = {
    "description": "The data broker is unavailable.",
    "type": int,
    "validate_fun": int
    }

try:
    from metadataStore.analysisapi.utility import listify
except ImportError:
    def listify(*args, **kwargs):
        err_msg = ("listify from metadataStore.analysis.utility is not "
                   "importable. run_header cannot be listified")
        print("userpackages/NSLS2/broker.py: {0}".format(err_msg))
        logger.warning(err_msg)


class BrokerQuery(Module):
    _settings = ModuleSettings(namespace="broker")

    _input_ports = [
        IPort(name="unique_query_dict",
              label="guaranteed unique query for the data broker",
              signature="basic:Dictionary"),
        IPort(name="query_dict", label="Query for the data broker",
              signature="basic:Dictionary"),
        IPort(name="is_returning_data", label="Return data with search results",
              signature="basic:Boolean", default=True)
    ]

    _output_ports = [
        OPort(name="query_result", signature="basic:Dictionary")
    ]

    def compute(self):
        if self.has_input("unique_query_dict"):
            query = self.get_input("unique_query_dict")
        elif self.has_input("query_dict"):
            query = self.get_input("query_dict")

        data = self.get_input("is_returning_data")
        query["data"] = data
        result = search(**query)
        self.set_output("query_result", result)


class Listify(Module):
    _settings = ModuleSettings(namespace="broker")

    _input_ports = [
        IPort(name="data_keys",
              label="The data key to turn in to a list",
              signature="basic:String"),
        IPort(name="run_header",
              label="Run header from the data broker",
              signature="basic:Dictionary"),
    ]

    _output_ports = [
        OPort(name="listified_data", signature="basic:List"),
        OPort(name="data_keys", signature="basic:List"),
        OPort(name="listified_time", signature="basic:List"),
    ]

    def compute(self):
        key = None
        if self.has_input("data_keys"):
            key = self.get_input("data_keys")
        header = self.get_input("run_header")
        data, keys, time = listify(data_keys=key, run_header=header)
        print('data ', data)
        print('keys ', keys)
        print('time ', time)
        # set the module's output
        self.set_output("data_keys", keys)
        self.set_output("listified_data", data)
        self.set_output("listified_time", time)


def vistrails_modules():
    return [BrokerQuery, Listify]
