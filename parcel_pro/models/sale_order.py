# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    QuoteId=fields.Char('QuoteId')
    ShipmentId=fields.Char('ShipmentId')
    ServiceCode=fields.Char('ServiceCode')
    PackageCode=fields.Char('PackageCode')
    TrackingNumber=fields.Char('TrackingNumber')
    FromParcelPro = fields.Boolean('From Parcel Pro')
    QuoteIdCreated = fields.Boolean('QuoteIdCreated')
    IsCod = fields.Boolean('IsCod')
    IsHighValueShipment = fields.Boolean('Is High Value Shipment')
    create_contact = fields.Boolean('Create/Update Contact',default=True)
    PickUpDate = fields.Date('PickUpDate')
    estimator_ids = fields.One2many('estimator', 'sale_order_id',
                                           string="Estimator")
    _sql_constraints = [
        ('unique_QuoteId', 'UNIQUE ("QuoteId")', 'QuoteId must be unique!'),
    ]

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.carrier_id.name == 'Parcel Pro':
                # if self.create_contact:
                #     print("===",self.create_contact)
                #     self.env['parcel.configuration'].post_contact(order,True)
                # else:
                self.env['parcel.configuration'].post_quotation(order)
        return res

    @api.model
    def process_create_quotation(self, ids=None):

        filters = [('QuoteIdCreated', '=', False),('state', '=', 'draft'),('carrier_id.name', '=', 'Parcel Pro')]
        order_rec = self.search(filters)
        res = None
        try:
            for order in order_rec:
                self.env['parcel.configuration'].post_contact(order)
        except Exception as e:
            _logger.exception("Failed processing %s "%e)
        return res

class Estimator(models.Model):
    _name = 'estimator'

    AccessorialsCost=fields.Float('AccessorialsCost')
    BaseRate=fields.Float('BaseRate')
    BusinessDaysInTransit=fields.Integer('BusinessDaysInTransit')
    DeliveryByTime=fields.Char('DeliveryByTime')
    ExceededMaxCoverage=fields.Boolean('ExceededMaxCoverage')
    EstimatorHeaderID=fields.Char('EstimatorHeaderID')
    sale_order_id = fields.Many2one("sale.order","QuoteID")
    estimator_detail_ids = fields.One2many('estimator.detail', 'estimator_id',string="Estimator Details")


class EstimatorDetail(models.Model):
    _name = 'estimator.detail'

    AccessorialDescription=fields.Char('AccessorialDescription')
    AccessorialFee=fields.Float('AccessorialFee')
    EstimatorDetailID=fields.Char('EstimatorDetailID',required=True)
    estimator_id = fields.Many2one("estimator","EstimatorHeaderID")
