# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    QuoteId=fields.Char('QuoteId')
    ShipmentId=fields.Char('ShipmentId')
    ServiceCode=fields.Char('ServiceCode')
    PackageCode=fields.Char('PackageCode')
    TrackingNumber=fields.Char('TrackingNumber')
    FromParcelPro = fields.Boolean('From Parcel Pro')
    IsCod = fields.Boolean('IsCod')
    PickUpDate = fields.Date('PickUpDate')
    _sql_constraints = [
        ('unique_QuoteId', 'UNIQUE ("QuoteId")', 'QuoteId must be unique!'),
    ]

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.carrier_id.name == 'Parcel Pro':
                self.env['parcel.configuration'].generate_quotation(order)
        return res


class EstimatorLine(models.Model):
    _name = 'estimator.line'

    AccessorialsCost=fields.Float('AccessorialsCost')
    BaseRate=fields.Float('BaseRate')
    BusinessDaysInTransit=fields.Integer('BusinessDaysInTransit')
    DeliveryByTime=fields.Boolean('DeliveryByTime')
    EstimatorHeaderID=fields.Float('EstimatorHeaderID')
    SaleOrderId = fields.Many2one("sale.order","Sale")
