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
    ContactType=fields.Integer('ContactType')
    UPSPickUpType=fields.Char('UPSPickUpType')
    IsUserDefault = fields.Boolean('IsUserDefault')
    IsExpress = fields.Boolean('IsExpress')
    IsResidential = fields.Boolean('IsResidential')
    State = fields.Char('State Code')
    Country = fields.Char('Country Code')
    FromParcelPro = fields.Boolean('From Parcel Pro')

