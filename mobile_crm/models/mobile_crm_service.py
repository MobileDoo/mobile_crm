"""Opportunities on mobile: a salesperson follows hers, a team leader the team's.

The list is the pipeline: the open opportunities of the scope, filtered by stage (chips in the app, `stages`
below), with the next step and whether it is late. The form, its buttons (Won, Lost with Odoo's own wizard,
new quotation...) and the stage bar come from the form view, so customer fields and modules follow along.
Notes and the next step go through the generic `/form/note`.
"""
from odoo import _, api, fields, models

# Open: not won yet (lost opportunities are archived by Odoo, so they leave the list on their own).
OPEN = [('stage_id.is_won', '=', False)]


class MobileCrmService(models.AbstractModel):
    _name = 'mobile.crm.service'
    _inherit = 'mobile.record.service'
    _description = 'Mobile CRM Service'

    _mobile_model = 'crm.lead'
    _mobile_feature = 'crm'
    _mobile_create_capability = 'create'
    _mobile_scope_capabilities = {'mine': 'view', 'followup': 'view', 'team': 'team'}
    _mobile_core_field_names = [
        'name', 'partner_id', 'partner_name', 'contact_name', 'phone', 'email_from', 'expected_revenue', 'probability',
        'stage_id', 'priority', 'user_id', 'team_id', 'date_deadline', 'description',
    ]
    _mobile_list_field_names = [
        'name', 'partner_id', 'partner_name', 'contact_name', 'phone', 'expected_revenue', 'company_currency',
        'probability', 'stage_id', 'priority', 'user_id', 'activity_state', 'activity_summary', 'activity_date_deadline',
    ]

    @api.model
    def _mobile_is_leader(self):
        return bool(self.env['crm.team'].search_count([('user_id', '=', self.env.uid)], limit=1))

    @api.model
    def _mobile_sees_team(self):
        user = self.env.user
        if not user.has_group('sales_team.group_sale_salesman'):
            return False
        return user.has_group('sales_team.group_sale_manager') or user.has_group(
            'sales_team.group_sale_salesman_all_leads') or self._mobile_is_leader()

    @api.model
    def _base_domain(self, scope):
        """What the scope shows, before the stage chip."""
        if scope == 'mine':
            return [('user_id', '=', self.env.uid)]
        if scope == 'followup':
            # Mine, and either nothing is planned or the next step is due: what to call back today.
            return [('user_id', '=', self.env.uid), ('stage_id.is_won', '=', False), '|',
                    ('activity_ids', '=', False), ('activity_state', 'in', ('overdue', 'today'))]
        if scope == 'team':
            if self.env.user.has_group('sales_team.group_sale_manager'):
                return []
            return [('team_id.user_id', '=', self.env.uid)]
        return None

    @api.model
    def _mobile_domain(self, scope, params):
        domain = list(self._base_domain(scope))
        chip = params.get('stage_id') if isinstance(params, dict) else None
        if scope != 'followup':
            if chip == 'won':
                domain.append(('stage_id.is_won', '=', True))
            elif isinstance(chip, int) and not isinstance(chip, bool):
                domain.append(('stage_id', '=', chip))
            else:
                domain += OPEN
        return domain

    @api.model
    def _mobile_search_domain(self, query):
        return ['|', '|', '|', '|', ('name', 'ilike', query), ('partner_id', 'ilike', query),
                ('partner_name', 'ilike', query), ('contact_name', 'ilike', query), ('phone', 'ilike', query)]

    @api.model
    def _mobile_order(self, scope):
        # Highest priority and soonest deadline first; the rest by expected revenue.
        return 'priority desc, date_deadline asc, expected_revenue desc, id desc'

    @api.model
    def _mobile_stages(self, scope):
        """Chips of the list: the stages with the number of opportunities of the scope in each (won ones last)."""
        Lead = self.env['crm.lead']
        domain = self._base_domain(scope)
        counts = {stage.id: count for stage, count in Lead._read_group(domain, groupby=['stage_id'],
                                                                        aggregates=['__count']) if stage}
        stages = self.env['crm.stage'].search([])
        result = [{'id': s.id, 'name': s.name, 'count': counts.get(s.id, 0), 'is_won': bool(s.is_won)}
                  for s in stages if counts.get(s.id) or not s.is_won]
        result.sort(key=lambda s: (s['is_won'], 0))
        return {
            'stages': result,
            'open': sum(s['count'] for s in result if not s['is_won']),
            'won': sum(s['count'] for s in result if s['is_won']),
        }

    @api.model
    def _mobile_new_context(self):
        return {'default_user_id': self.env.uid, 'default_type': 'opportunity'}
