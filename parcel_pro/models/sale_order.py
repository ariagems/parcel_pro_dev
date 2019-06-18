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
    # ShipmentId = fields.Char('ShipmentId')
    ReferenceNumber = fields.Char("ReferenceNumber")
    CustomerReferenceNumber = fields.Char("CustomerReferenceNumber")
    # TrackingNumber = fields.Char('TrackingNumber')

    ParcelPro = fields.Boolean('From Parcel Pro')
    QuoteIdCreated = fields.Boolean('QuoteIdCreated')
    UpdateAddressBook = fields.Boolean('UpdateAddressBook')
    ShipToResidential = fields.Boolean('ShipToResidential')
    IsCod = fields.Boolean('IsCod')
    IsHighValueShipment = fields.Boolean('Is High Value Shipment')
    IsHighValueShipmentPosted = fields.Boolean('Is High Value Shipment Post')

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
        p_excep = self.env['parcel.pro.exceptions']
        for order in self:
            if order.carrier_id.parcel_pro == True:
                print("In actio confirm....",order)
                if not self.order_line:
                    p_excep.create({'name': order.name, 'api_type': 'post_quotation',
                                    'message': "There should be at least one product in line."})
                    return False
                    # raise ValidationError(_('There should be at least one product in line.'))
                post_quotation = self.env['parcel.configuration'].post_quotation(order)
                print("Post Quote.................",post_quotation)
                if not post_quotation:
                    return False
                res = super(SaleOrder, self).action_confirm()
                for pick in order.picking_ids:
                    print("pick........",pick)
                    pick.write({'QuoteId':order.QuoteId,'ParcelPro':True,'IsHighValueShipment':order.IsHighValueShipment,
                    'IsHighValueShipmentPosted':order.IsHighValueShipmentPosted,'IsCod':order.IsCod,'CarrierCode':order.CarrierCode,
                      'ServiceCode':order.ServiceCode.id,'PackageCode':order.PackageCode.id,'ShipDate':order.ShipDate,
                                'Height' :order.Height, 'Width' :order.Width,'Length' :order.Length, 'Weight' :order.Weight})
                return res
            else:
                return  super(SaleOrder, self).action_confirm()

    @api.model
    def process_create_quotation(self, ids=None):
        filters = [('state', '=', 'draft'),('QuoteIdCreated', '=', False),('carrier_id.parcel_pro', '=', True)]
        order_rec = self.search(filters)
        print("=========== order_rec ============================",order_rec)
        res = None
        if order_rec:
            try:
                p_ids = self.env['parcel.pro.exceptions'].search([('api_type', '=', 'post_quotation')])
                p_ids.unlink()
                for order in order_rec:
                    print("@@ process_create_quotation order @@@@@@@@@@@@@@@@@@@.............",order)
                    order.action_confirm()
                    # self.env['parcel.configuration'].post_quotation(order)
            except Exception as e:
                _logger.exception("Failed processing %s "%e)
        return res

class Estimator(models.Model):
    _name = 'estimator'

    AccessorialsCost=fields.Float('Accessorials Cost')
    BaseRate=fields.Float('Base Rate')
    BusinessDaysInTransit=fields.Integer('Business Days InTransit')
    DeliveryByTime=fields.Char('Delivery By Time')
    ExceededMaxCoverage=fields.Boolean('Exceeded Max Coverage')
    EstimatorHeaderID=fields.Char('Estimator Header ID')
    sale_order_id = fields.Many2one("sale.order","Quote ID")
    estimator_detail_ids = fields.One2many('estimator.detail', 'estimator_id',string="Estimator Details")

class EstimatorDetail(models.Model):
    _name = 'estimator.detail'

    AccessorialDescription=fields.Char('Accessorial Description')
    AccessorialFee=fields.Float('Accessorial Fee')
    EstimatorDetailID=fields.Char('Estimator Detail ID',required=True)
    estimator_id = fields.Many2one("estimator","Estimator Header ID")

class CarrierServices(models.Model):
    _name = 'carrier.services'

    CarrierCode = fields.Selection([('1', 'UPS'), ('2', 'FEDEX')], string='CarrierCode',required=True)
    DomesticOnly=fields.Boolean()
    MaxCoverage=fields.Char("Max Coverage")
    name=fields.Char("Service Code",required=True)
    ServiceCodeDesc=fields.Char()

class PackageServices(models.Model):
    _name = 'package.services'

    CarrierCode = fields.Selection([('0', 'Not Set'),('1', 'UPS'), ('2', 'FEDEX'),('3', 'DHL'),('4', 'USPS')], string='CarrierCode')
    name=fields.Char("Package Type Code",required=True)
    PackageTypeDesc=fields.Char("Package Type Desc",required=True)
    CarrierServiceCode=fields.Char("Carrier Service Code",required=True)
