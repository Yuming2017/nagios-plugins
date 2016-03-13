#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2016-01-25 10:11:51 +0000 (Mon, 25 Jan 2016)
#
#  https://github.com/harisekhon/nagios-plugins
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn
#  and optionally send me feedback
#
#  https://www.linkedin.com/in/harisekhon
#

"""

Nagios Plugin to check the status of an Oozie server via the HTTP Rest API

Tested on Hortonworks HDP 2.3.2 and 2.4.0

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import json
import os
import sys
import traceback
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'pylib'))
sys.path.append(libdir)
try:
    # pylint: disable=wrong-import-position
    from harisekhon.utils import UnknownError, support_msg_api
    from harisekhon.utils import validate_host, validate_port, isJson
    from harisekhon import RequestHandler
    from harisekhon import NagiosPlugin
except ImportError as _:
    print(traceback.format_exc(), end='')
    sys.exit(4)

__author__ = 'Hari Sekhon'
__version__ = '0.3'

class OozieStatusCheck(NagiosPlugin):

    def add_options(self):
        self.add_hostoption(name='Oozie', default_host='localhost', default_port=11000)

    def run(self):
        self.no_args()
        host = self.get_opt('host')
        port = self.get_opt('port')
        validate_host(host)
        validate_port(port)

        url = 'http://%(host)s:%(port)s/oozie/v1/admin/status' % locals()
        req = RequestHandler().get(url)
        # should == NORMAL
        if not isJson(req.content):
            raise UnknownError('non-JSON returned by Oozie server at {0}:{1}'.format(host, port))
        status = None
        try:
            _ = json.loads(req.content)
            status = _['systemMode']
        except KeyError:
            raise UnknownError('systemMode key was not returned in output from Oozie. {0}'.format(support_msg_api()))
        self.msg = 'Oozie status = {0}'.format(status)
        if status == 'NORMAL':
            self.ok()
        else:
            self.critical()


if __name__ == '__main__':
    OozieStatusCheck().main()
