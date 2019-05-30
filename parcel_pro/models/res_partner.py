# -*- coding: utf-8 -*-

from openerp import exceptions, fields, models,api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    NickName=fields.Char('NickName')
    FirstName=fields.Char('FirstName')
    LastName=fields.Char('LastName')
    FaxNo=fields.Char('FaxNo')
    ContactId=fields.Char('ContactId')
    CustomerId=fields.Char('CustomerId')
    ApartmentSuite=fields.Char('ApartmentSuite')
    ProvinceRegion=fields.Char('ProvinceRegion')
    ContactType = fields.Selection([
        ('0', 'Null -0'),
        ('1', 'CorporateContact-1'),
        ('2', 'MailingContact-2'),
        ('3', 'Location-3'),
        ('4', 'APContact-4'),
        ('11', 'AddressBook-11'),
        ('12', 'BillingAddress-12'),
    ], "ContactType", default="0")
    UPSPickUpType = fields.Selection([
        ('0', 'Ocassional'),
        ('1', 'RequestPending'),
        ('2', 'DailyPickUp'),
        ('3', 'DailyOnRoutePickUp'),
        ('4', 'DaySpecificPickUp'),
        ('5', 'SmartPickUp'),
    ], "UPSPickUpType", default="0")
    IsUserDefault = fields.Boolean('IsUserDefault')
    IsExpress = fields.Boolean('IsExpress')
    IsResidential = fields.Boolean('IsResidential')
    State = fields.Char('State Code')
    Country = fields.Char('Country Code')
    FromParcelPro = fields.Boolean('From Parcel Pro')
    contact_created = fields.Boolean('Contact Created')
    TotalContacts = fields.Char('TotalContacts')
    UserId = fields.Char('UserId')
    # contact_type = fields.Selection([
    #     ('ShipFrom', 'ShipFrom'),
    #     ('ShipTo', 'ShipTo'),
    # ], "Location Type", default="0")


    _sql_constraints = [
        ('unique_ContactId', 'UNIQUE ("ContactId")', 'ContactId must be unique!'),
    ]

    @api.multi
    def action_post_contact(self):
        self.env['parcel.configuration'].post_contact(self)
        return True

    @api.onchange('country_id')
    def _onchange_country_id(self):
        super(ResPartner, self)._onchange_country_id()
        if self.country_id:
            self.Country = self.country_id.code

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id
        self.State = self.state_id.code



