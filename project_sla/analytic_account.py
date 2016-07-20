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

from openerp import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class AnalyticAccount(models.Model):
    """ Add SLA to Analytic Accounts """
    _inherit = 'account.analytic.account'

    sla_ids = fields.Many2many('project.sla', string='Service Level Agreement')

    @api.multi
    def _reapply_sla(self, recalc_closed=False):
        """
        Force SLA recalculation on open documents that already are subject to
        this SLA Definition.
        To use after changing a Contract SLA or it's Definitions.
        The ``recalc_closed`` flag allows to also recompute closed documents.
        """
        ctrl_obj = self.env['project.sla.control']
        for contract in self.browse(self._ids):
            # for each contract, and for each model under SLA control ...
            ctrl_models = set([self.env[sla.control_model.model] for sla in contract.sla_ids])
            for model in ctrl_models:
                base = [] if recalc_closed else [('stage_id.fold', '=', 0)]
                doc_ids = []
                if 'analytic_account_id' in model._columns:
                    domain = base + [('analytic_account_id', '=', contract.id)]
                    doc_ids += model.search(domain)
                if 'project_id' in model._columns:
                    domain = base + [('project_id.analytic_account_id', '=', contract.id)]
                    doc_ids += model.search(domain)
                if doc_ids:
                    docs = model.browse(doc_ids)
                    ctrl_obj.store_sla_control(docs)
        return True

    @api.multi
    def reapply_sla(self):
        """ Reapply SLAs button action """
        return self._reapply_sla()
