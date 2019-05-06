# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from openerp.exceptions import ValidationError
from openerp import api, exceptions, fields, models, _
import requests
import json
from base64 import encode

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))
        self._action_confirm()
        if self.carrier_id:
        	print('iiiiiiiiii',self.carrier_id)
        	val=self.carrier_id.response_key(self.partner_id, self)
        	print("valvalvalval",val)
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()
        return True
    pro_QuoteId=fields.Char('Pro QuoteId')