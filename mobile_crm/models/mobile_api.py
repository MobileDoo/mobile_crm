from odoo import _, api, models


class MobileApi(models.AbstractModel):
    _inherit = 'mobile.api'

    @api.model
    def _mobile_features(self):
        return super()._mobile_features() + ['crm']

    @api.model
    def _mobile_record_services(self):
        return dict(super()._mobile_record_services(), crm='mobile.crm.service')

    @api.model
    def _mobile_access(self):
        access = super()._mobile_access()
        user = self.env.user
        if not self.env['crm.lead'].has_access('read'):
            return access
        capabilities = {
            'view': user.has_group('sales_team.group_sale_salesman'),
            'create': self.env['crm.lead'].has_access('create') and user.has_group('sales_team.group_sale_salesman'),
            # The pipeline of the teams the user leads (all of them for sales managers).
            'team': self.env['mobile.crm.service']._mobile_sees_team(),
        }
        if capabilities['view']:
            access['crm'] = capabilities
        return access

    @api.model
    def _mobile_home_tiles(self):
        return super()._mobile_home_tiles() + [
            {'key': 'crm_mine', 'label': _('My opportunities'), 'feature': 'crm', 'capability': 'view', 'sequence': 62},
            {'key': 'crm_followup', 'label': _('Follow up'), 'feature': 'crm', 'capability': 'view', 'sequence': 63},
            {'key': 'crm_team', 'label': _('Team pipeline'), 'feature': 'crm', 'capability': 'team', 'sequence': 64},
        ]

    @api.model
    def _mobile_home_tabs(self):
        return super()._mobile_home_tabs() + [
            {'key': 'opportunities', 'label': _('Opportunities'), 'feature': 'crm', 'capability': 'view',
             'sequence': 61},
        ]
