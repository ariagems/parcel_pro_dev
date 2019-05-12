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
    create_contact = fields.Boolean('Create/Update Contact',default=True)
    PickUpDate = fields.Date('PickUpDate')
    _sql_constraints = [
        ('unique_QuoteId', 'UNIQUE ("QuoteId")', 'QuoteId must be unique!'),
    ]

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.carrier_id.name == 'Parcel Pro':
                if self.create_contact:
                    print("===",self.create_contact)
                    self.env['parcel.configuration'].post_contact(order,True)
                else:
                    self.env['parcel.configuration'].post_quotation(order,order.partner_id.ContactId,order.partner_shipping_id.ContactId)
        return res


class EstimatorLine(models.Model):
    _name = 'estimator.line'

    AccessorialsCost=fields.Float('AccessorialsCost')
    BaseRate=fields.Float('BaseRate')
    BusinessDaysInTransit=fields.Integer('BusinessDaysInTransit')
    DeliveryByTime=fields.Boolean('DeliveryByTime')
    EstimatorHeaderID=fields.Float('EstimatorHeaderID')
    SaleOrderId = fields.Many2one("sale.order","Sale")
