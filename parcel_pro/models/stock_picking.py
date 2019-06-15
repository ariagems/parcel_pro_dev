# -*- coding: utf-8 -*-

from openerp import exceptions, fields, models
from openerp import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)
import requests

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.addons import decimal_precision as dp

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    QuoteId=fields.Char('Quote Id')
    ShipmentId=fields.Char('Shipment Id')
    TrackingNumber=fields.Char('Tracking Number')
    ParcelPro = fields.Boolean('Parcel Pro Method')
    ShipmentId_created = fields.Boolean('Shipment Created')
    IsHighValueShipment = fields.Boolean('Is High Value Shipment')
    IsHighValueShipmentPosted = fields.Boolean('Is High Value Shipment Post')
    IsHighValueShipment_Approved = fields.Boolean('Is High ValueShipment Approved')
    IsCod = fields.Boolean('IsCod')
    CarrierCode = fields.Selection([('1', 'UPS'), ('2', 'FEDEX'),('3', 'DHL'),('4', 'USPS')], string='CarrierCode')
    ServiceCode = fields.Many2one('carrier.services',"Service Code")
    PackageCode = fields.Many2one('package.services',"Package Code")
    ShipDate = fields.Date(string='Ship Date', default=(str(datetime.now() + relativedelta(days=1))))
    Height = fields.Float()
    Width = fields.Float()
    Length = fields.Float()
    Weight = fields.Float()
    LabelImage = fields.Binary(string="Label Image")

    @api.multi
    def action_done(self):
        if self.ParcelPro:
            if self.IsHighValueShipment and not self.IsHighValueShipment_Approved:
                result = self.env['parcel.configuration'].get_high_value_queue(self.QuoteId)
                print("result..",result)
                if not result.get('Status')!= 2:
                    raise ValidationError(_('High Value Queue not Approved by parcel pro.'))
                else:
                    self.IsHighValueShipment_Approved = True
            self.env['parcel.configuration'].post_shipment(self)
        res = super(StockPicking, self).action_done()
        return res

    @api.model
    def process_create_shipment(self, ids=None):
        filters = [('QuoteIdCreated', '=', False),('state', '=', 'draft'),('carrier_id.name', '=', 'Parcel Pro')]
        shipment_rec = self.search(filters)
        res = None
        try:
            for order in shipment_rec:
                self.env['parcel.configuration'].post_contact(order, True)
        except Exception as e:
            _logger.exception("Failed processing %s "%e)
        return res

class StockMove(models.Model):
    _inherit = 'stock.move'

    height = fields.Float(compute='_cal_move_height', digits=dp.get_precision('Stock Height'), store=True)
    length = fields.Float(compute='_cal_move_length', digits=dp.get_precision('Stock Length'), store=True)
    width = fields.Float(compute='_cal_move_width', digits=dp.get_precision('Stock Width'), store=True)

    @api.depends('product_id', 'product_uom_qty', 'product_uom')
    def _cal_move_height(self):
        for move in self.filtered(lambda moves: moves.product_id.height > 0.00):
            move.height = (move.product_qty * move.product_id.height)

    @api.depends('product_id', 'product_uom_qty', 'product_uom')
    def _cal_move_length(self):
        for move in self.filtered(lambda moves: moves.product_id.length > 0.00):
            move.length = (move.product_qty * move.product_id.length)

    @api.depends('product_id', 'product_uom_qty', 'product_uom')
    def _cal_move_width(self):
        for move in self.filtered(lambda moves: moves.product_id.width > 0.00):
            move.width = (move.product_qty * move.product_id.width)