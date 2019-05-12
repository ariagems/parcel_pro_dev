# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class ParcelProApiWizard(models.TransientModel):

    _name = 'parcel.pro.api.wizard'

    name = fields.Char('Name')
    date =fields.Date('Date', default=fields.Date.context_today,readonly=True)
    api_type = fields.Selection([
        ('generate_session', 'Generate Session'),
        ('getgenerate_multi_contacts', 'Get Multiple Contacts'),
        ('getgenerate_single_contact', 'Get Single Contact'),
        ('get_shipment', 'Get Shipment'),
        ('get_shipment_label', 'Get Shipment Label'),
        ('get_high_value_queue', 'Get High Value Queue'),
    ], "API Type",default="generate_session",required=True)
    create_contact = fields.Boolean('Create Contact In Database')
    ContactId = fields.Char('ContactId')
    QuoteId = fields.Char('QuoteId')
    ShipmentID = fields.Char('ShipmentID')

    def action_fetch_data(self):
        parcel_config_rec = self.env['parcel.configuration']
        parcel_pro_resp_rec = self.env['parcel.pro.response']
        if self.api_type == 'generate_session':
            result = parcel_config_rec.generate_session()
        elif self.api_type == 'getgenerate_multi_contacts':
            result = parcel_config_rec.get_contacts(self.create_contact)
        elif self.api_type == 'getgenerate_single_contact':
            result = parcel_config_rec.get_contact(self.ContactId,self.create_contact)
        elif self.api_type == 'get_shipment':
            result = parcel_config_rec.get_shipment(self.ShipmentID)
        elif self.api_type == 'get_shipment_label':
            result = parcel_config_rec.get_shipment(self.ShipmentID)
        elif self.api_type == 'get_high_value_queue':
            result = parcel_config_rec.get_high_value_queue(self.QuoteId)
        print("=== Final Result =====",result)
        view_id = parcel_pro_resp_rec.create({'name':self.api_type,'message':result})
        return {'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': view_id.id,
                'res_model': 'parcel.pro.response',
                'target': 'self',
                }

class ParcelProResponse(models.Model):

    _name = "parcel.pro.response"

    name = fields.Char('API Name')
    message = fields.Text('Message')
    date = fields.Date('Date', default=fields.Date.context_today, readonly=True)

