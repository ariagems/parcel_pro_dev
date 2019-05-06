# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from openerp.exceptions import ValidationError
from openerp import api, exceptions, fields, models, _
import requests
import json
from base64 import encode

class Respartner(models.Model):
    _inherit = 'res.partner'

    customer_id=fields.Char('Customer ID')
    nick_name=fields.Char('NickName')
    first_name=fields.Char('FirstName')
    last_name=fields.Char('LastName')
    fax_no=fields.Char('FaxNo')
    contact_id=fields.Char('ContactId')
    is_express=fields.Boolean('IsExpress')
    apartment_suite=fields.Char('ApartmentSuite')
    province_region=fields.Char('ProvinceRegion')
    is_user_defalut=fields.Boolean('IsUserDefault')
    total_contact=fields.Char('TotalContacts')
    contact_type=fields.Integer('ContactType')
    ups_pick_uptype=fields.Integer('UPSPickUpType')
    is_residential=fields.Boolean('IsResidential')

    # @api.model
    # def create(self, vals):
    #     session = self.env['parcelpro.api'].search([])
    #     var_session = session.session_id
    #     headers = {"content-type": "application/json"}

    #     crt_url = 'https://apibeta.parcelpro.com/v1/location?sessionID=' + var_session
    #     crt_data = {
    #         "ApartmentSuite": "",
    #         "City": vals.get("city"),
    #         "CompanyName": "Comapny Name",
    #         "ContactId": "NOID",
    #         "Country": "US",
    #         "CustomerId": "",
    #         "Email": vals.get("email"),
    #         "FaxNo": vals.get('fax_no'),
    #         "FirstName": vals.get("name"),
    #         "IsExpress": vals.get('is_express'),
    #         "IsResidential": vals.get('is_residential'),
    #         "LastName": vals.get("name"),
    #         "NickName": vals.get("name"),
    #         "State": "CA",
    #         "StreetAddress": vals.get("street") + vals.get("street2"),
    #         "TelephoneNo": vals.get("phone"),
    #         "Zip": vals.get("zip")
    #     }
    #     convDict = json.dumps(crt_data)
    #     crt_res = requests.request("POST", crt_url, data=convDict, headers=headers)
    #     crt_get = json.loads(crt_res.text)
    #     print("::::::::::::::::::::::;ccccccccccccc_res:::::::::::::::::::::::::::::::::::::::::::", crt_res)
    #     print("::::::::::::::::::::::;ccccccccccccc_res:::::::::::::::::::::::::::::::::::::::::::", crt_get)
    #     print("::::::::::::::::::::::;:::::::::::::::::::::::::::::::::::::::::::", )
    #     print("::::::::::::::::::::::;:::::::::::::::::::::::::::::::::::::::::::", )
    #     print("::::::::::::::::::::::;:::::::::::::::::::crt_get.get('IsExpress')::::::::::::::::::::::::",type(crt_get.get('IsExpress')))
    #     print("::::::::::::::::::::::;:::::::::::::::::::self.is_express::::::::::::::::::::::::",self.is_express)




        # vals['customer_id'] = crt_get.get('CustomerId')
        # vals['nick_name'] = crt_get.get('NickName')
        # vals['fax_no'] = crt_get.get('FaxNo')
        # vals['contact_id'] = crt_get.get('ContactId')
        # vals['is_express'] = crt_get.get('IsExpress')
        # vals['apartment_suite'] = crt_get.get('ApartmentSuite')
        # vals['province_region'] = crt_get.get('ProvinceRegion')
        # vals['is_user_defalut'] = crt_get.get('IsUserDefault')
        # vals['total_contact'] = crt_get.get('TotalContacts')
        # vals['contact_type'] = crt_get.get('ContactType')
        # vals['ups_pick_uptype'] = crt_get.get('UPSPickUpType')
        # vals['is_residential'] = crt_get.get('IsResidential')

        # vals['customer_id'] = self.env['ir.sequence'].next_by_code('res.partner') or _('New')
        # result = super(Respartner, self).create(vals)
        # return result

    @api.multi
    def unlink(self):
        print ("::::::::::::::::::::self.contact_id:::::::::::::::::::::::::;",self.contact_id)
        session = self.env['parcelpro.api'].search([])
        var_session = session.session_id
        headers = {"content-type": "application/json"}

        if self.contact_id:
            delete_url = 'https://apibeta.parcelpro.com/v1/location/delete/'+self.contact_id+'?sessionID='+var_session
            del_res = requests.request("POST", delete_url, headers=headers)
            # the_dictsss = json.loads(del_res.text)
            print ("::::::::::::::::::::::;del_res:::::::::::::::::::::::::::::::::::::::::::",del_res)
            # print ("::::::::::::::::::::::;the_dictsss:::::::::::::::::::::::::::::::::::::::::::",the_dictsss)
            return super(Respartner, self).unlink()
        else:
            return super(Respartner, self).unlink()


    @api.onchange('first_name','last_name')
    def _onchange_name(self):
    	name=self.first_name
    	if self.last_name:
    		name=name +'  '+str(self.last_name)
    	self.name=name
