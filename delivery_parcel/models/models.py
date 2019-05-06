# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from openerp.exceptions import ValidationError
from openerp import api, exceptions, fields, models, _
import requests
import json
from base64 import encode


class Dynamic_Location_Date(models.TransientModel):
    _name = "contacts.wizard"

    @api.multi
    def get_parcelpro_contacts(self):
        session = self.env['parcelpro.api'].search([])
        var_session = session.session_id
        url_contact = 'https://apibeta.parcelpro.com/v1/location?sessionID='+var_session
        headers = {"content-type": "application/json"}
        contact_response = requests.request("GET", url_contact, headers=headers)
        contact_dict = json.loads(contact_response.text)
        for dictionary in contact_dict:
            dic_contacts = 'https://apibeta.parcelpro.com/v1/location/'+dictionary['ContactId']+'?sessionID='+var_session
            dic_response = requests.request("GET", dic_contacts, headers=headers)
            dict_list = json.loads(dic_response.text)
            find_contact = self.env['res.partner'].search([('contact_id','=',dict_list['ContactId'])])
            print ("::::::::::::::::::::::;find::::::::::::::::::::::",find_contact)
            if not find_contact:
                partner_obj = self.env['res.partner']
                partner_obj_fileds = partner_obj.fields_get()
                partner_default_value = partner_obj.default_get(partner_obj_fileds)
                partner_default_value.update({
                    'first_name': dict_list['FirstName'],
                    'last_name': dict_list['LastName'],
                    'street': dict_list['StreetAddress'] and dict_list['StreetAddress'] or "",
                    'city': dict_list['City'] and dict_list['City'] or "",
                    'phone': dict_list['TelephoneNo'],
                    'email': dict_list['Email'] and dict_list['Email'] or "",
                    'nick_name': dict_list['NickName'] and dict_list['NickName'] or "",
                    'contact_id': dict_list['ContactId'] and dict_list['ContactId'] or "",
                    'contact_type': dict_list['ContactType'] and dict_list['ContactType'] or "",
                    'total_contact': dict_list['TotalContacts'] and dict_list['TotalContacts'] or "",
                    'apartment_suite': dict_list['ApartmentSuite'] and dict_list['ApartmentSuite'] or "",
                })
                create_contact = partner_obj.create(partner_default_value)
                print (":::::::::::::::::::::::::create_contact::::::::::::::::::::::::::::::::",partner_default_value)
            else:
                partner_obj = self.env['res.partner']
                update_contact = partner_obj.write({
                    'first_name': dict_list['FirstName'],
                    'last_name': dict_list['LastName'],
                    'street': dict_list['StreetAddress'] and dict_list['StreetAddress'] or "",
                    'city': dict_list['City'] and dict_list['City'] or "",
                    'phone': dict_list['TelephoneNo'],
                    'email': dict_list['Email'] and dict_list['Email'] or "",
                    'nick_name': dict_list['NickName'] and dict_list['NickName'] or "",
                    'contact_id': dict_list['ContactId'] and dict_list['ContactId'] or "",
                    'contact_type': dict_list['ContactType'] and dict_list['ContactType'] or "",
                    'total_contact': dict_list['TotalContacts'] and dict_list['TotalContacts'] or "",
                    'apartment_suite': dict_list['ApartmentSuite'] and dict_list['ApartmentSuite'] or "",
                })
                print (":::::::::::::::::::::update_contact::::::::::::::::::::",update_contact)


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    package_carrier_type = fields.Selection(selection_add=[('parcel', 'Parcel')])

class delivery_parcel(models.Model):
    _inherit = 'delivery.carrier'

    #delivery_type = fields.Selection(selection_add=[('parcel', 'Parcel')])
    parcel_username = fields.Char(string='Parcel Username')
    parcel_passwd = fields.Char(string='Parcel Password')
    parcel_access_number = fields.Char(string='Parcel AccessLicenseNumber')
    parcel_package_weight_unit = fields.Selection([('LBS', 'Pounds'), ('KGS', 'Kilograms')], default='LBS' ,string='Parcel Package Weight Unit')
    parcel_package_dimension_unit = fields.Selection([('IN', 'Inches'), ('CM', 'Centimeters')], string="Units for Parcel Package Size", default='IN')
    parcel_label_file_type = fields.Selection([('GIF', 'PDF'),
                                            ('ZPL', 'ZPL'),
                                            ('EPL', 'EPL'),
                                            ('SPL', 'SPL')],
                                           string="Parcel Label File Type", default='GIF', oldname='x_label_file_type')



    @api.multi
    def response_key(self, partner, sale):
        # :::::::::::::::::::::::::::::::::::Authentication::::::::::::::::::::::::::::::::::::
        url = 'https://apibeta.parcelpro.com/v1/auth?username=' + self.parcel_username + '&password=' + self.parcel_passwd + '&apikey=' + self.parcel_access_number
        headers = {"content-type": "application/json"}
        response = requests.request("GET", url, headers=headers)
        parcel_dict = json.loads(response.text)


        # ::::::::::::::::::::::::::::::::::::Get::Contactss::location::::::::::::::::::::::::::::::::::
        url_contact = 'https://apibeta.parcelpro.com/v1/location?sessionID='+parcel_dict.get('SessionID')
        # responsesss = requests.request("GET", url_contact, headers=headers)
        # the_dict = json.loads(responsesss.text)
        # for dictionary in the_dict:
        #     url_contactss = 'https://apibeta.parcelpro.com/v1/location/'+dictionary['ContactId']+'?sessionID='+parcel_dict.get('SessionID')
        #     responsesss = requests.request("GET", url_contactss, headers=headers)
        #     the_dictsss = json.loads(responsesss.text)
        #     print ("::::::::::::::::::::::;the_dictsss:::::::::::::::::::::;",the_dictsss)
        # ::::::::::::::::::::::::::::::::::::Create::location::::::::::::::::::::::::::::::::::::
        crt_url = 'https://apibeta.parcelpro.com/v1/location?sessionID='+parcel_dict.get('SessionID')
        
        crt_data = {
                "ApartmentSuite":"",
                "City":"Nadiad",
                "CompanyName":"",
                "ContactId":"",
                "Country": "US",
                "CustomerId":"",
                "Email":partner.email,
                "FaxNo":partner.fax_no or "",
                "FirstName":partner.first_name,
                "IsExpress":False,
                "IsResidential":True,
                "LastName":partner.last_name,
                "NickName":partner.nick_name,
                "State":"CA",
                "StreetAddress":partner.street,
                "TelephoneNo":partner.phone,
                "Zip":"90241"
            }
        
        print('GGGGGGGGGGGGGG',crt_data, crt_url)
        convDict = json.dumps(crt_data)
        print('TTTTTTTTTTTTTTTT',convDict)
        crt_res = requests.request("POST", crt_url ,data=convDict,headers=headers)
        crt_get = json.loads(crt_res.text)
        if crt_get:
            partner.customer_id= crt_get.get('CustomerId')
            partner.contact_id = crt_get.get('ContactId')
            partner.is_express = crt_get.get('IsExpress')
            partner.apartment_suite = crt_get.get('ApartmentSuite')
            partner.province_region = crt_get.get('ProvinceRegion')
            partner.is_user_defalut = crt_get.get('IsUserDefault')
            partner.total_contact = crt_get.get('TotalContacts')
            partner.contact_type = crt_get.get('ContactType')
            partner.ups_pick_uptype = crt_get.get('UPSPickUpType')
            partner.is_residential = crt_get.get('IsResidential')
        crt_quote ='https://apibeta.parcelpro.com/v1/quote?sessionID='+parcel_dict.get('SessionID') 
        
        null = None
        false=False
        true=True
        crt_quote_data = {
                       "ShipmentId":"NOID",
                       "QuoteId":"",
                       "CustomerId":"NOID",
                       "UserId":"NOID",
                       "ShipToResidential":false,
                       "ServiceCode":"01-DOM",
                       "CarrierCode":2,
                       "ShipTo":{
                          "ContactId":"NOID",
                          "CustomerId":"",
                          "UserId":"",
                          "ContactType":11,
                          "CompanyName":"Test Company",
                          "FirstName":"Matt",
                          "LastName":"Jones",
                          "StreetAddress":"1101 Beach Blvd",
                          "ApartmentSuite":"",
                          "ProvinceRegion":"",
                          "City":"LA PALMA",
                          "State":"CA",
                          "Country":"US",
                          "Zip":"90623",
                          "TelephoneNo":"7145551212",
                          "FaxNo":"",
                          "Email":"",
                          "NickName":"",
                          "IsExpress":false,
                          "IsResidential":false,
                          "IsUserDefault":false,
                          "UPSPickUpType":0,
                          "TotalContacts":"0"
                       },
                       "UpdateAddressBook":false,
                       "NotifyRecipient":false,
                       "ShipFrom":{
                          "ContactId":"NOID",
                          "CustomerId":"",
                          "UserId":"",
                          "ContactType":3,
                          "CompanyName":"Acme Jewelry",
                          "FirstName":"DDDDDDDDDDDDDDDD",
                          "LastName":"N72",
                          "StreetAddress":"10011 Holmgren Road",
                          "ApartmentSuite":"",
                          "ProvinceRegion":"",
                          "City":"ONEIDA",
                          "State":"WI",
                          "Country":"US",
                          "Zip":"54155",
                          "TelephoneNo":"9205551212",
                          "FaxNo":"",
                          "Email":"",
                          "NickName":"Dikuuuuuuuuuuuuuuuuu",
                          "IsExpress":false,
                          "IsResidential":false,
                          "IsUserDefault":false,
                          "UPSPickUpType":0,
                          "TotalContacts":"0"
                       },
                       "ShipDate":"2019-04-30",
                       "PackageCode":"MEDIUM BOX",
                       "Height":0,
                       "Width":0,
                       "Length":0,
                       "Weight":10.0,
                       "InsuredValue":20.0,
                       "IsSaturdayPickUp":false,
                       "IsSaturdayDelivery":false,
                       "IsDeliveryConfirmation":false,
                       "IsCod":false,
                       "CodAmount":0.0,
                       "IsSecuredCod":false,
                       "IsRegularPickUp":false,
                       "IsDropoff":true,
                       "IsPickUpRequested":false,
                       "IsSmartPickUp":false,
                       "PickUpContactName":"",
                       "PickUpTelephone":"",
                       "PickUpAtHour":"",
                       "PickUpAtMinute":"",
                       "PickUpByHour":"",
                       "PickUpByMinute":"",
                       "PickUpDate":"",
                       "DispatchConfirmationNumber":"",
                       "DispatchLocation":"",
                       "NotifySender":false,
                       "ReferenceNumber":"",
                       "TrackingNumber":"",
                       "CustomerReferenceNumber":"",
                       "IsDirectSignature":false,
                       "IsThermal":true,
                       "IsMaxCoverageExceeded":false,
                       "Estimator":[
        
                       ],
                       "LabelImage":null,
                       "IsBillToThirdParty":false,
                       "BillToThirdPartyPostalCode":"",
                       "BillToAccount":"",
                       "IsShipFromRestrictedZip":false,
                       "IsShipToRestrictedZip":false,
                       "IsShipToHasRestrictedWords":false,
                       "IsShipFromHasRestrictedWords":false,
                       "IsHighValueShipment":false,
                       "IsHighValueReport":false,
                       "ReceivedBy":"",
                       "ReceivedTime":"",
                       "TotalShipments":"0"
                    }
        # header = {"Content-type": "application/x-www-form-urlencoded",
        #   "Accept": "text/plain"} 
        print('uuuuuuuuuuuuuuuuuuu',crt_quote)
        print('crt_quote_datacrt_quote_data',crt_quote_data)
        quote_Dict =json.dumps(crt_quote_data)
        print('99999999999999999',quote_Dict)
        quote_res = requests.post(crt_quote, data=quote_Dict,headers=headers)
        #quote_res = requests.request("POST", crt_quote ,data=quote_Dict,headers=headers)
        print('bbbbb',quote_res)
        quote_get = json.loads(quote_res.text)
        if quote_get:
           sale.pro_QuoteId=quote_get.get('QuoteId')
        print (":::::::::::::::::::::::::::Generates a quoteid and rate information::::::::::::::::::::::",quote_res)
        print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print ("::::::::::::::::::::::::::::Response:::::::::::::::::::::::::::::::::::::::::::::::::::::::",quote_get.get('QuoteId'))
        print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
class ParcelproConfig(models.Model):

    _name = "parcelpro.api"
    api_uname = fields.Char("Username",required=True)
    api_pwd = fields.Char("Password",required=True)
    api_key = fields.Char(string="API Key from Parcelpro", required=True)
    session_id = fields.Char(string="Session ID")

    @api.multi
    def response_key(self):
        # :::::::::::::::::::::::::::::::::::Authentication::::::::::::::::::::::::::::::::::::
        url = 'https://apibeta.parcelpro.com/v1/auth?username=' + self.api_uname + '&password=' + self.api_pwd + '&apikey=' + self.api_key
        headers = {"content-type": "application/json"}
        response = requests.request("GET", url, headers=headers)
        parcel_dict = json.loads(response.text)
        self.write({'session_id': parcel_dict.get('SessionID')})

        # ::::::::::::::::::::::::::::::::::::Get::Contactss::location::::::::::::::::::::::::::::::::::
        url_contact = 'https://apibeta.parcelpro.com/v1/location?sessionID='+parcel_dict.get('SessionID')
        responsesss = requests.request("GET", url_contact, headers=headers)
        the_dict = json.loads(responsesss.text)
        # for dictionary in the_dict:
        #     url_contactss = 'https://apibeta.parcelpro.com/v1/location/'+dictionary['ContactId']+'?sessionID='+parcel_dict.get('SessionID')
        #     responsesss = requests.request("GET", url_contactss, headers=headers)
        #     the_dictsss = json.loads(responsesss.text)
        #     print ("::::::::::::::::::::::;the_dictsss:::::::::::::::::::::;",the_dictsss)




        # ::::::::::::::::::::::::::::::::::::Delete::location::::::::::::::::::::::::::::::::::::
        # delete_url = 'https://apibeta.parcelpro.com/v1/location/delete/92F72BFC-F7AA-4B12-AC9F-92550AD00FCB?sessionID='+parcel_dict.get('SessionID')
        # del_res = requests.request("POST", delete_url, headers=headers)
        # the_dictsss = json.loads(responsesss.text)
        # print ("::::::::::::::::::::::;del_res:::::::::::::::::::::::::::::::::::::::::::",del_res)




        # ::::::::::::::::::::::::::::::::::::Create::location::::::::::::::::::::::::::::::::::::
        # crt_url = 'https://apibeta.parcelpro.com/v1/location?sessionID='+parcel_dict.get('SessionID')
        # crt_data = {
        #         "ApartmentSuite":"",
        #         "City":"Nadiad",
        #         "CompanyName":"vimal gupta",
        #         "ContactId":"NOID",
        #         "Country":"US",
        #         "CustomerId":"",
        #         "Email":"drp.dkn72@gmail.com",
        #         "FaxNo":"",
        #         "FirstName":"Sara",
        #         "IsExpress":False,
        #         "IsResidential":True,
        #         "LastName":"Millan",
        #         "NickName":"SaritaMillan",
        #         "State":"CA",
        #         "StreetAddress":"11637 BELLFLOWER BLVD",
        #         "TelephoneNo":"5626445975",
        #         "Zip":"90241"
        #     }
        # convDict = json.dumps(crt_data)
        # crt_res = requests.request("POST", crt_url ,data=convDict,headers=headers)
        # crt_get = json.loads(crt_res.text)
        # print ("::::::::::::::::::::::;ccccccccccccc_res:::::::::::::::::::::::::::::::::::::::::::",crt_res)
        # print ("::::::::::::::::::::::;ccccccccccccc_res:::::::::::::::::::::::::::::::::::::::::::",crt_get)
        #




        # crt_address = 'https://apibeta.parcelpro.com/v1/addressbook?sessionID='+parcel_dict.get('SessionID')
        # delete_address = 'https://apibeta.parcelpro.com/<version>/addressbook/delete/[LOCATIONID]?sessionID='+parcel_dict.get('SessionID')
        # crt_data = {
        #     "ApartmentSuite": "",
        #     "City": "Downey",
        #     "CompanyName": "vimal",
        #     "ContactId": "NOID",
        #     "ContactType": "11",
        #     "Country": "US",
        #     "CustomerId": "",
        #     "Email": "drp.dkn72@gmail.com",
        #     "FaxNo": "",
        #     "FirstName": "Sara",
        #     "IsResidential": True,
        #     "LastName": "Millan",
        #     "NickName": "SaritaMillan",
        #     "ProvinceRegion": "",
        #     "State": "CA",
        #     "StreetAddress": "11637 BELLFLOWER BLVD",
        #     "TelephoneNo": "5626445975",
        #     "UserId": "10618",
        #     "Zip": "90241"
        # }
        # convDict = json.dumps(crt_data)
        # crt_res = requests.request("POST", crt_address, data=convDict ,headers=headers)
        # crt_get = json.loads(crt_res.text)
        # print ("::::::::::::::::::::::;del_res:::::::::::::::::::::::::::::::::::::::::::",crt_get)






        #::::::::::::::::::::::::::::::::::::Create::Quote::::::::::::::::::::::::::::::::::::
        crt_quote ='https://apibeta.parcelpro.com/v1/quote?sessionID='+parcel_dict.get('SessionID')       
        
        
        null = None
        false=False
        true=True
        crt_quote_data = {
                       "ShipmentId":"NOID",
                       "QuoteId":"",
                       "CustomerId":"NOID",
                       "UserId":"NOID",
                       "ShipToResidential":false,
                       "ServiceCode":"01-DOM",
                       "CarrierCode":2,
                       "ShipTo":{
                          "ContactId":"NOID",
                          "CustomerId":"",
                          "UserId":"",
                          "ContactType":11,
                          "CompanyName":"Test Company",
                          "FirstName":"Matt",
                          "LastName":"Jones",
                          "StreetAddress":"1101 Beach Blvd",
                          "ApartmentSuite":"",
                          "ProvinceRegion":"",
                          "City":"LA PALMA",
                          "State":"CA",
                          "Country":"US",
                          "Zip":"90623",
                          "TelephoneNo":"7145551212",
                          "FaxNo":"",
                          "Email":"",
                          "NickName":"",
                          "IsExpress":false,
                          "IsResidential":false,
                          "IsUserDefault":false,
                          "UPSPickUpType":0,
                          "TotalContacts":"0"
                       },
                       "UpdateAddressBook":false,
                       "NotifyRecipient":false,
                       "ShipFrom":{
                          "ContactId":"NOID",
                          "CustomerId":"",
                          "UserId":"",
                          "ContactType":3,
                          "CompanyName":"Acme Jewelry",
                          "FirstName":"DDDDDDDDDDDDDDDD",
                          "LastName":"N72",
                          "StreetAddress":"10011 Holmgren Road",
                          "ApartmentSuite":"",
                          "ProvinceRegion":"",
                          "City":"ONEIDA",
                          "State":"WI",
                          "Country":"US",
                          "Zip":"54155",
                          "TelephoneNo":"9205551212",
                          "FaxNo":"",
                          "Email":"",
                          "NickName":"Dikuuuuuuuuuuuuuuuuu",
                          "IsExpress":false,
                          "IsResidential":false,
                          "IsUserDefault":false,
                          "UPSPickUpType":0,
                          "TotalContacts":"0"
                       },
                       "ShipDate":"2019-04-30",
                       "PackageCode":"MEDIUM BOX",
                       "Height":0,
                       "Width":0,
                       "Length":0,
                       "Weight":10.0,
                       "InsuredValue":20.0,
                       "IsSaturdayPickUp":false,
                       "IsSaturdayDelivery":false,
                       "IsDeliveryConfirmation":false,
                       "IsCod":false,
                       "CodAmount":0.0,
                       "IsSecuredCod":false,
                       "IsRegularPickUp":false,
                       "IsDropoff":true,
                       "IsPickUpRequested":false,
                       "IsSmartPickUp":false,
                       "PickUpContactName":"",
                       "PickUpTelephone":"",
                       "PickUpAtHour":"",
                       "PickUpAtMinute":"",
                       "PickUpByHour":"",
                       "PickUpByMinute":"",
                       "PickUpDate":"",
                       "DispatchConfirmationNumber":"",
                       "DispatchLocation":"",
                       "NotifySender":false,
                       "ReferenceNumber":"",
                       "TrackingNumber":"",
                       "CustomerReferenceNumber":"",
                       "IsDirectSignature":false,
                       "IsThermal":true,
                       "IsMaxCoverageExceeded":false,
                       "Estimator":[
        
                       ],
                       "LabelImage":null,
                       "IsBillToThirdParty":false,
                       "BillToThirdPartyPostalCode":"",
                       "BillToAccount":"",
                       "IsShipFromRestrictedZip":false,
                       "IsShipToRestrictedZip":false,
                       "IsShipToHasRestrictedWords":false,
                       "IsShipFromHasRestrictedWords":false,
                       "IsHighValueShipment":false,
                       "IsHighValueReport":false,
                       "ReceivedBy":"",
                       "ReceivedTime":"",
                       "TotalShipments":"0"
                    }
        # header = {"Content-type": "application/x-www-form-urlencoded",
        #   "Accept": "text/plain"} 
        print('uuuuuuuuuuuuuuuuuuu',crt_quote)
        print('crt_quote_datacrt_quote_data',crt_quote_data)
        quote_Dict =json.dumps(crt_quote_data)
        print('99999999999999999',quote_Dict)
        quote_res = requests.post(crt_quote, data=quote_Dict,headers=headers)
        #quote_res = requests.request("POST", crt_quote ,data=quote_Dict,headers=headers)
        print('bbbbb',quote_res)
        quote_get = json.loads(quote_res.text)
        print (":::::::::::::::::::::::::::Generates a quoteid and rate information::::::::::::::::::::::",quote_res)
        print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print ("::::::::::::::::::::::::::::Response:::::::::::::::::::::::::::::::::::::::::::::::::::::::",quote_get.get('QuoteId'))
        print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")

        # ::::::::::::::::::::::::::::::::::::Cancels or Delete Quote::::::::::::::::::::::::::::::::::::::
        # delete_quote = 'https://apibeta.parcelpro.com/v1/quote/delete/A27F185D-CC4E-4D9E-9AED-DFED1F78E8B3?sessionID='+parcel_dict.get('SessionID')
        # res_delete_quote = requests.request("POST", delete_quote, headers=headers)
        # the_dict_quote = json.loads(responsesss.text)
        # print (":::::::::::::::::::::::::::Cancels the quote ::::::::::::::::::::::",res_delete_quote)
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print ("::::::::::::::::::::::::::::Response:::::::::::::::::::::::::::::::::::::::::::::::::::::::",the_dict_quote)
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")


        # ::::::::::::::::::::::::::::::::::::Books a shipment and generates a label and tracking number::::::::::::::::::::::::::::::::::
        # url_shipment = 'https://apibeta.parcelpro.com/v1/shipment/'+quote_get.get('QuoteId')+'?sessionID=' + parcel_dict.get('SessionID')
        # respons_shipment = requests.request("POST", url_shipment, headers=headers)
        # shipment_dict = json.loads(respons_shipment.text)
        # print (":::::::::::::::::::::::::::Books a shipment and generates a label and tracking number::::::::::::::::::::::", respons_shipment)
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print ("::::::::::::::::::::::::::::Response:::::::::::::::::::::::::::::::::::::::::::::::::::::::",shipment_dict)
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")

        # ::::::::::::::::::::::::::::::::::::Retrieves shipment information specified ID::::::::::::::::::::::::::::::::::
        # get_shipment_data = 'https://apibeta.parcelpro.com/v1/shipment/491dc1b5-df0f-4341-ac42-7f629be49f01?sessionID=' + parcel_dict.get('SessionID')
        # get_shipment_respons = requests.request("GET", get_shipment_data, headers=headers)
        # get_shipment_dict = json.loads(get_shipment_respons.text)
        # print (":::::::::::::::::::::::::::Retrieves shipment information specified ID::::::::::::::::::::::", get_shipment_respons)
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print ("::::::::::::::::::::::::::::Response:::::::::::::::::::::::::::::::::::::::::::::::::::::::",get_shipment_dict)
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")


        # ::::::::::::::::::::::::::::::::::::Retrieves the shipment label specified ID::::::::::::::::::::::::::::::::::
        # get_shipment_lable_data = 'https://apibeta.parcelpro.com/v1/shipment/label?shipmentId=491dc1b5-df0f-4341-ac42-7f629be49f01&sessionID=' + parcel_dict.get('SessionID')
        # get_shipment_lable_respons = requests.request("GET", get_shipment_lable_data, headers=headers)
        # get_shipment_lable_dict = json.loads(get_shipment_lable_respons.text)
        # print (":::::::::::::::::::::::::::Retrieves the shipment label specified ID::::::::::::::::::::::", get_shipment_lable_respons)
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print ("::::::::::::::::::::::::::::Response:::::::::::::::::::::::::::::::::::::::::::::::::::::::",get_shipment_lable_dict)
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")




        # ::::::::::::::::::::::::::::::::::::Retrieves retrieve the first 25 shipments::::::::::::::::::::::::::::::::::
        # retrieve_shipment_data = 'https://apibeta.parcelpro.com/v1/shipment?pageindex=1&pagesize=25&sessionID=' + parcel_dict.get('SessionID')
        # retrieve_shipment_respons = requests.request("GET", retrieve_shipment_data, headers=headers)
        # retrieve_shipment_dict = json.loads(retrieve_shipment_respons.text)
        # print (":::::::::::::::::::::::::::Retrieves retrieve the first 25 shipments::::::::::::::::::::::", retrieve_shipment_respons)
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print ("::::::::::::::::::::::::::::Response:::::::::::::::::::::::::::::::::::::::::::::::::::::::",retrieve_shipment_dict)
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")


        # ::::::::::::::::::::::::::::::::::::Voids the booked Delete shipment specified ::::::::::::::::::::::::::::::::::::
        # voids_shipment_url = 'https://apibeta.parcelpro.com/v1/shipment/delete/491dc1b5-df0f-4341-ac42-7f629be49f01?sessionID='+parcel_dict.get('SessionID')
        # voids_shipment_res = requests.request("POST", voids_shipment_url, headers=headers)
        # print (":::::::::::::::::::::::::::Voids the booked Delete shipment specified ID::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print ("::::::::::::::::::::::::::::Response:::::::::::::::::::::::::::::::::::::::::::::::::::::::",voids_shipment_res)
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")






        # ::::::::::::::::::::::::::::::::::::Submit a package for approval and check the status of the high value package::::::::::::::::::::::::::::::::::
        # get_high_value_package_data = 'https://apibeta.parcelpro.com/<version>/highvalue/[QUOTEID]' + parcel_dict.get('SessionID')
        # get_high_value_package_data = 'https://apibeta.parcelpro.com/v1/highvalue/4F474354-0F98-441A-9317-6C4BCD434581?sessionID='+parcel_dict.get('SessionID')
        # get_high_value_package_respons_post = requests.request("POST", get_high_value_package_data, headers=headers)
        # get_high_value_package_respons = requests.request("GET", get_high_value_package_data, headers=headers)
        # get_high_value_package_dict = json.loads(get_high_value_package_respons_post.text)
        # print (":::::::::::::::::::::::::::approval and check the status of the high value package::::::::::::::::::::::", get_high_value_package_respons_post)
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print ("::::::::::::::::::::::::::::Response:::::::::::::::::::::::::::::::::::::::::::::::::::::::",get_high_value_package_dict)
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")











        # print ("::::::::::::::parcel_dict.get('SessionID'):::::::::::::::::::::;",parcel_dict.get('SessionID'))
        # crt_shop = 'https://apibeta.parcelpro.com/v1/estimator?sessionID='+parcel_dict.get('SessionID')
        # crt_shop_data = {
        #                "ShipToResidential":False,
        #                "ShipTo":{
        #                   "ContactId":"23EA85D3-66B8-4817-883B-565B23707998",
        #                   "CustomerId":"",
        #                   "UserId":"",
        #                   "ContactType":11,
        #                   "CompanyName":"Test Company",
        #                   "FirstName":"Matt",
        #                   "LastName":"Jones",
        #                   "StreetAddress":"1101 Beach Blvd",
        #                   "ApartmentSuite":"",
        #                   "ProvinceRegion":"",
        #                   "City":"LA PALMA",
        #                   "State":"CA",
        #                   "Country":"US",
        #                   "Zip":"90623",
        #                   "TelephoneNo":"7145551212",
        #                   "FaxNo":"",
        #                   "Email":"",
        #                   "NickName":"",
        #                   "IsExpress":False,
        #                   "IsResidential":False,
        #                   "IsUserDefault":False,
        #                   "UPSPickUpType":0,
        #                   "TotalContacts":"0"
        #                },
        #                "ShipFrom":{
        #                   "ContactId":90241,
        #                   "CustomerId":"",
        #                   "UserId":"",
        #                   "ContactType":3,
        #                   "CompanyName":"Acme Jewelry",
        #                   "FirstName":"Erin",
        #                   "LastName":"Rogers",
        #                   "StreetAddress":"10011 Holmgren Road",
        #                   "ApartmentSuite":"",
        #                   "ProvinceRegion":"",
        #                   "City":"ONEIDA",
        #                   "State":"WI",
        #                   "Country":"US",
        #                   "Zip":"54155",
        #                   "TelephoneNo":"9205551212",
        #                   "FaxNo":"",
        #                   "Email":"",
        #                   "NickName":"Other",
        #                   "IsExpress":False,
        #                   "IsResidential":False,
        #                   "IsUserDefault":False,
        #                   "UPSPickUpType":0,
        #                   "TotalContacts":"0"
        #                },
        #                "Height":0,
        #                "Width":0,
        #                "Length":0,
        #                "Weight":10.0,
        #                "InsuredValue":20.0,
        #                "IsSaturdayPickUp":False,
        #                "IsSaturdayDelivery":False,
        #                "IsDeliveryConfirmation":False,
        #                "IsCod":False,
        #                "CodAmount":0.0,
        #                "IsSecuredCod":False,
        #                "IsRegularPickUp":False,
        #                "IsDropoff":True,
        #             }
        # shop_dict = json.dumps(crt_shop_data)
        # shop_res = requests.request("POST", crt_shop ,data=shop_dict,headers=headers)
        # shop_get = json.loads(shop_res.text)
        # print (":::::::::::::::::::::::::::Generates Shop information::::::::::::::::::::::",shop_res)
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print ("::::::::::::::::::::::::::::Response:::::::::::::::::::::::::::::::::::::::::::::::::::::::",shop_get)
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")







        # if parcel_dict.get('SessionID'):
        #     raise exceptions.Warning("ParcelPro Connected..!!")
        # else:
        #     raise exceptions.Warning("ParcelPro Not Connected...!!")





