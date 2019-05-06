# -*- coding: utf-8 -*-

from openerp import exceptions, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    QuoteId=fields.Char('QuoteId')
    ShipmentId=fields.Char('ShipmentId')
    ServiceCode=fields.Char('ServiceCode')
    TrackingNumber=fields.Char('TrackingNumber')
    FromParcelPro = fields.Boolean('From Parcel Pro')
    IsCod = fields.Boolean('IsCod')
    PickUpDate = fields.Boolean('PickUpDate')

class EstimatorLine(models.Model):
    _name = 'estimator.line'

    AccessorialsCost=fields.Float('AccessorialsCost')
    BaseRate=fields.Float('BaseRate')
    BusinessDaysInTransit=fields.Integer('BusinessDaysInTransit')
    DeliveryByTime=fields.Boolean('DeliveryByTime')
    EstimatorHeaderID=fields.Float('EstimatorHeaderID')
    SaleOrderId = fields.Many2one("sale.order","Sale")
