# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Daniel Reis
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, api, models


class SLADefinition(models.Model):
    """
    SLA Definition
    """
    _name = 'project.sla'
    _description = 'SLA Definition'

    name = fields.Char('Title', size=64, required=True, translate=True)
    active = fields.Boolean('Active', default=True)
    control_model = fields.Many2one('ir.model', string="Control Model", required=True)
    control_field_id = fields.Many2one('ir.model.fields', 'Control Date', required=True,
                                       domain="[('model_id', '=', control_model), ('ttype', 'in', ['date', 'datetime'])]",
                                       help="Date field used to check if the SLA was achieved.")
    sla_line_ids = fields.One2many('project.sla.line', 'sla_id', 'Definitions')
    analytic_ids = fields.Many2many('account.analytic.account', string='Contracts')

    @api.onchange('control_model')
    def _onchange_control_model(self):
        self.control_field_id = ''
        return {'control_field_id': {'domain': ['model_id', '=', self.control_model]}}

    @api.multi
    def _reapply_sla(self, recalc_closed=False):
        """
        Force SLA recalculation on all _open_ Contracts for the selected SLAs.
        To use upon SLA Definition modifications.
        """
        for account in self.browse(self._ids):
            account._reapply_sla(recalc_closed=recalc_closed)
        return True

    @api.multi
    def reapply_sla(self):
        """ Reapply SLAs button action """
        return self._reapply_slas()


class SLARules(models.Model):
    """
    SLA Definition Rule Lines
    """
    _name = 'project.sla.line'
    _definition = 'SLA Definition Rule Lines'
    _order = 'sequence'

    sla_id = fields.Many2one('project.sla', 'SLA Definition')
    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char('Title', size=64, required=True, translate=True)
    condition = fields.Char('Condition', size=256,
                            help="Apply only if this expression is evaluated to True. "
                                 "The document fields can be accessed using either o, "
                                 "obj or object. Example: obj.priority <= '2'")
    limit_qty = fields.Integer('Hours to Limit')
    warn_qty = fields.Integer('Hours to Warn')
