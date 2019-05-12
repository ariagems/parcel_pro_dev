# -*- coding: utf-8 -*-

from openerp import exceptions, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    QuoteId=fields.Char('QuoteId')
    ShipmentId=fields.Char('ShipmentId')
    TrackingNumber=fields.Char('TrackingNumber')
    FromParcelPro = fields.Boolean('From Parcel Pro')
    IsCod = fields.Boolean('IsCod')