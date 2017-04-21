##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""
OGC OWS and WPS Exceptions

Based on OGC OWS, WPS and

http://lists.opengeospatial.org/pipermail/wps-dev/2013-October/000335.html
"""


from werkzeug.exceptions import HTTPException
from werkzeug._compat import text_type
from werkzeug.utils import escape

import logging

from pywps import __version__

__author__ = "Alex Morega & Calin Ciociu"

LOGGER = logging.getLogger('PYWPS')


class NoApplicableCode(HTTPException):
    """No applicable code exception implementation

    also

    Base exception class
    """

    code = 400
    locator = ""

    def __init__(self, description, locator="", code=400):
        self.code = code
        self.description = description
        self.locator = locator
        msg = 'Exception: code: %s, locator: %s, description: %s' % (self.code, self.description, self.locator)
        LOGGER.exception(msg)

        HTTPException.__init__(self)

    @property
    def name(self):
        """The status name."""
        return self.__class__.__name__

    def get_headers(self, environ=None):
        """Get a list of headers."""
        return [('Content-Type', 'text/xml')]

    def get_description(self, environ=None):
        """Get the description."""
        if self.description:
            return '''<ows:ExceptionText>%s</ows:ExceptionText>''' % escape(self.description)
        else:
            return ''

    def get_body(self, environ=None):
        """Get the XML body."""
        return text_type((
            u'<?xml version="1.0" encoding="UTF-8"?>\n'
            u'<!-- PyWPS %(version)s -->\n'
            u'<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/ows/1.1 http://schemas.opengis.net/ows/1.1.0/owsExceptionReport.xsd" version="1.0.0">\n'  # noqa
            u'  <ows:Exception exceptionCode="%(name)s" locator="%(locator)s" >\n'
            u'      %(description)s\n'
            u'  </ows:Exception>\n'
            u'</ows:ExceptionReport>'
        ) % {
            'version': __version__,
            'code': self.code,
            'locator': escape(self.locator),
            'name': escape(self.name),
            'description': self.get_description(environ)
        })


class InvalidParameterValue(NoApplicableCode):
    """Invalid parameter value exception implementation
    """
    code = 400


class MissingParameterValue(NoApplicableCode):
    """Missing parameter value exception implementation
    """
    code = 400


class FileSizeExceeded(NoApplicableCode):
    """File size exceeded exception implementation
    """
    code = 400


class VersionNegotiationFailed(NoApplicableCode):
    """Version negotiation exception implementation
    """
    code = 400


class OperationNotSupported(NoApplicableCode):
    """Operation not supported exception implementation
    """
    code = 501


class StorageNotSupported(NoApplicableCode):
    """Storage not supported exception implementation
    """
    code = 400


class NotEnoughStorage(NoApplicableCode):
    """Storage not supported exception implementation
    """
    code = 400


class ServerBusy(NoApplicableCode):
    """Max number of operations exceeded
    """

    code = 400
    description = 'Maximum number of processes exceeded'

    def get_body(self, environ=None):
        """Get the XML body."""
        return text_type((
            u'<?xml version="1.0" encoding="UTF-8"?>\n'
            u'<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/ows/1.1 ../../../ows/1.1.0/owsExceptionReport.xsd" version="1.0.0">'  # noqa
            u'<ows:Exception exceptionCode="%(name)s">'
            u'%(description)s'
            u'</ows:Exception>'
            u'</ows:ExceptionReport>'
        ) % {
            'name': escape(self.name),
            'description': self.get_description(environ)
            }
        )
