from odoo import http
from odoo.http import request

from odoo.addons.mobile_connector.controllers.utils import MobileApiError, mobile_route, require_access


class MobileCrmController(http.Controller):

    @mobile_route('/mobile/api/v1/crm/stages')
    def stages(self, payload):
        """Stages with the number of opportunities of a scope in each: the chips above the list."""
        service = request.env['mobile.crm.service']
        scope = payload.get('scope') or 'mine'
        capability = service._mobile_scope_capabilities.get(scope)
        if not capability:
            raise MobileApiError('bad_request', f'scope must be one of {", ".join(service._mobile_scope_capabilities)}')
        require_access('crm', capability)
        return service._mobile_stages(scope)
