# -*- coding: utf-8 -*-

from openerp import exceptions, fields, models
from openerp import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    QuoteId=fields.Char('QuoteId')
    ShipmentId=fields.Char('ShipmentId')
    TrackingNumber=fields.Char('TrackingNumber')
    FromParcelPro = fields.Boolean('From Parcel Pro')
    IsHighValueShipment = fields.Boolean('From Parcel Pro')
    IsHighValueShipment_Approved = fields.Boolean('From Parcel Pro')
    IsCod = fields.Boolean('IsCod')

    @api.multi
    def action_done(self):
        print("class ......inherit......")
        res = super(StockPicking, self).action_done()
        print("Action done......inherit............")
        if self.FromParcelPro :
            if self.IsHighValueShipment and not self.IsHighValueShipment_Approved:
                if self.QuoteId:
                    result = self.env['parcel.configuration'].get_high_value_queue(self.QuoteId)
                    if not result.get('Status')!= 2:
                        raise ValidationError(_('High Value Queue not Approved by parcel pro.'))
                    else:
                        self.IsHighValueQueue_Approved = True
                        return self.env['parcel.configuration'].post_shipment(self.QuoteId)
                else:
                    raise ValidationError(_('NO QuoteId for this shipment.'))
            else:
                self.env['parcel.configuration'].post_shipment(self.QuoteId)

        return True


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