# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError




class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    parcel_pro = fields.Boolean('Parcel Pro')

    _sql_constraints = [
        ('unique_parcel_pro', 'UNIQUE ("parcel_pro")', 'Parcel Pro Method must be unique!'),
    ]


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    CarrierCode = fields.Selection([('1', 'UPS'), ('2', 'FEDEX'),('3', 'DHL'),('4', 'USPS')], string='CarrierCode')
    # ServiceCode=fields.Char('ServiceCode')
    ServiceCode = fields.Many2one('carrier.services',"ServiceCode")
    PackageCode = fields.Many2one('package.services',"PackageCode")
    # PackageCode=fields.Char('PackageCode')
    ShipDate = fields.Date(string='ShipDate', default=(str(datetime.now() + relativedelta(days=1))))

    QuoteId = fields.Char('QuoteId')
    ShipmentId = fields.Char('ShipmentId')
    ReferenceNumber = fields.Char("ReferenceNumber")
    CustomerReferenceNumber = fields.Char("CustomerReferenceNumber")
    TrackingNumber = fields.Char('TrackingNumber')

    ParcelPro = fields.Boolean('From Parcel Pro')
    QuoteIdCreated = fields.Boolean('QuoteIdCreated')

    UpdateAddressBook = fields.Boolean('UpdateAddressBook')

    ShipToResidential = fields.Boolean('ShipToResidential')
    IsCod = fields.Boolean('IsCod')
    IsHighValueShipment = fields.Boolean('Is High Value Shipment')

    InsuredValueThreshold = fields.Char('InsuredValueThreshold')
    InsuredValueMultiplier = fields.Char('InsuredValueMultiplier')

    IsSaturdayPickUp = fields.Boolean("IsSaturdayPickUp")
    IsSaturdayDelivery = fields.Boolean("IsSaturdayDelivery")
    IsDeliveryConfirmation = fields.Boolean("IsDeliveryConfirmation")
    IsSecuredCod = fields.Boolean("IsSecuredCod")
    IsRegularPickUp = fields.Boolean()
    IsDropoff = fields.Boolean()
    IsSmartPickUp = fields.Boolean()
    IsPickUpRequested = fields.Boolean()
    PickUpDate = fields.Date(string='PickUpDate')
    PickUpContactName = fields.Char()
    PickUpTelephone = fields.Char()
    PickUpAtHour = fields.Char()
    PickUpAtMinute = fields.Char()
    PickUpByHour = fields.Char()
    PickUpByMinute = fields.Char()

    DispatchConfirmationNumber = fields.Char()
    DispatchLocation = fields.Char()

    NotifyRecipient = fields.Boolean()
    NotifySender = fields.Boolean()

    IsDirectSignature = fields.Boolean()
    IsThermal = fields.Boolean()
    IsMaxCoverageExceeded = fields.Boolean()

    IsBillToThirdParty = fields.Boolean()
    BillToThirdPartyPostalCode = fields.Char()
    BillToAccount = fields.Char()
    IsShipFromRestrictedZip = fields.Boolean()
    IsShipToRestrictedZip = fields.Boolean()
    IsShipToHasRestrictedWords = fields.Boolean()
    IsShipFromHasRestrictedWords = fields.Boolean()
    IsHighValueReport = fields.Boolean()
    ReceivedBy = fields.Char()
    ReceivedTime = fields.Char()

    Height=fields.Float()
    Width=fields.Float()
    Length=fields.Float()
    Weight= fields.Float()
    estimator_ids = fields.One2many('estimator','sale_order_id',string="Estimator")

    _sql_constraints = [
        ('unique_QuoteId', 'UNIQUE ("QuoteId")', 'QuoteId must be unique!'),
    ]

    @api.onchange('carrier_id')
    def onchange_carrier_id(self):
        super(SaleOrder, self).onchange_carrier_id()
        if self.state in ('draft', 'sent'):
            self.delivery_price = 0.0
            self.delivery_rating_success = False
            self.delivery_message = False
        self.ParcelPro =  self.carrier_id.parcel_pro

    @api.onchange('CarrierCode')
    def onchange_CarrierCode(self):
        self.ServiceCode = False
        self.PackageCode = False
        return {}

    @api.multi
    def action_confirm(self):
        if not self.order_line:
            raise ValidationError(_('There should be at least one product in line.'))
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.carrier_id.parcel_pro == True:
                if order.PickUpDate and order.PickUpDate > order.ShipDate:
                    raise ValidationError(_('ShipDate should be greater than pickUp date.'))
                if order.partner_id.id == order.partner_shipping_id.id:
                    raise ValidationError(_('ShipFrom and ShipTo should be different location.'))
                if order.Weight <= 0:
                    raise ValidationError(_('Weight should be greater than 0'))
                self.env['parcel.configuration'].post_quotation(order)
        return res

    @api.model
    def process_create_quotation(self, ids=None):
        filters = [('QuoteIdCreated', '=', False),('state', '=', 'draft'),('carrier_id.name', '=', 'Parcel Pro')]
        order_rec = self.search(filters)
        res = None
        try:
            for order in order_rec:
                self.env['parcel.configuration'].post_quotation(order)
        except Exception as e:
            _logger.exception("Failed processing %s "%e)
        return res


# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     InsuredValue = fields.Float('InsuredValue')

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

class CarrierServices(models.Model):
    _name = 'carrier.services'

    CarrierCode = fields.Selection([('1', 'UPS'), ('2', 'FEDEX')], string='CarrierCode',required=True)
    DomesticOnly=fields.Boolean()
    MaxCoverage=fields.Char()
    name=fields.Char("ServiceCode",required=True)
    ServiceCodeDesc=fields.Char()

class PackageServices(models.Model):
    _name = 'package.services'

    CarrierCode = fields.Selection([('1', 'UPS'), ('2', 'FEDEX'),('3', 'DHL'),('4', 'USPS')], string='CarrierCode')
    name=fields.Char("PackageCode",required=True)
