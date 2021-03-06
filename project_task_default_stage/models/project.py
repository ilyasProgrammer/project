# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    case_default = fields.Boolean(
        string='Default for New Projects',
        help='If you check this field, this stage will be proposed by default '
             'on each new project. It will not assign this stage to existing '
             'projects.')


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.model
    def _get_type_common(self):
        ids = self.env['project.task.type'].search([('case_default', '=', True)])
        return ids

    type_ids = fields.Many2many(
        comodel_name='project.task.type', relation='project_task_type_rel',
        column1='project_id', column2='type_id', string='Tasks Stages',
        states={
            'close': [('readonly', True)],
            'cancelled': [('readonly', True)]
        }, default=_get_type_common
    )
