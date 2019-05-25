# -*- coding: utf-8 -*-

from openerp import exceptions, fields, models

class Respartner(models.Model):
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
        ('0', 'Null'),
        ('1', 'CorporateContact'),
        ('2', 'MailingContact'),
        ('3', 'Location'),
        ('4', 'APContact'),
        ('11', 'AddressBook'),
        ('12', 'BillingAddress'),
    ], "ContactType", default="0", required=True)
    UPSPickUpType = fields.Selection([
        ('0', 'Ocassional'),
        ('1', 'RequestPending'),
        ('2', 'DailyPickUp'),
        ('3', 'DailyOnRoutePickUp'),
        ('4', 'DaySpecificPickUp'),
        ('5', 'SmartPickUp'),
    ], "UPSPickUpType", default="0", required=True)
    IsUserDefault = fields.Boolean('IsUserDefault')
    IsExpress = fields.Boolean('IsExpress')
    IsResidential = fields.Boolean('IsResidential')
    State = fields.Char('State Code')
    Country = fields.Char('Country Code')
    FromParcelPro = fields.Boolean('From Parcel Pro')
    TotalContacts = fields.Char('TotalContacts')

    _sql_constraints = [
        ('unique_ContactId', 'UNIQUE ("ContactId")', 'ContactId must be unique!'),
    ]

