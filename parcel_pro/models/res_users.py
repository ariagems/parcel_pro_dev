# -*- coding: utf-8 -*-

from openerp import exceptions, fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    UserId=fields.Char('User Id')

