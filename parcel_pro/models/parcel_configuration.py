# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from odoo.exceptions import ValidationError
import requests
import json
import datetime

class ParcelConfiguration(models.Model):

    _name = "parcel.configuration"

    name = fields.Char("Name")
    user_name = fields.Char("User Name",required=True)
    password = fields.Char("Password",required=True)
    api_key = fields.Char(string="API Key", required=True)
    session = fields.Char(string="Session ID")
    quote_param = fields.Text(string="Quotation Parameter")

    def get_response(self, url,type,data_dict):
        result={}
        try:
            if type=="GET":
                headers = {"content-type": "application/json"}
                response = requests.request(type, url, headers=headers)
                result = json.loads(response.text)
            elif type =="POST":
                param_data = json.dumps(data_dict)
                print("Parameters in convert json.......",param_data)
                print("url..",url)
                headers = {"content-type": "application/json"}
                response = requests.post(url, data=param_data, headers=headers)
                result = json.loads(response.text)
        except ValidationError as e:
            raise ValidationError(_('There is something wrong ! %s ') % e.name)
        return result

    def generate_session(self):
        parcel_config_rec = self.search([])
        result = {}
        if parcel_config_rec:
            result['user_name'] = parcel_config_rec[0].user_name
            result['password'] = parcel_config_rec[0].password
            result['api_key'] = parcel_config_rec[0].api_key
            url = 'https://apibeta.parcelpro.com/v1/auth?username=' + parcel_config_rec[0].user_name + '&password=' + parcel_config_rec[0].password + '&apikey=' + parcel_config_rec[0].api_key
            result = self.get_response(url, "GET",{})
            if result.get('SessionID'):
                parcel_config_rec.write({'session':result.get('SessionID')})
                result["remark"] = "This session Id is updated in Odoo Configuration"
        else:
            raise ValidationError(_('There is no configuration found for API !'))
        return result

    def get_session(self):
        parcel_config_rec = self.search([],limit=1)
        if parcel_config_rec and parcel_config_rec[0].session:
            return parcel_config_rec[0].session
        else:
            raise ValidationError(_('There is no session found for API in Configuration '))

    # def create_contact(self,data):
    #     state_id = False
    #     country_id = False
    #     customer_rec = self.env['res.partner'].search([('ContactId', '=', data.get('ContactId'))], limit=1)
    #     if customer_rec:
    #         return {"message": "Contact Already Exist", "ContactId": data.get('ContactId')}
    #     else:
    #         try:
    #             data["mobile"] = data.get("TelephoneNo")
    #             data["fax"] = data.get("FaxNo")
    #             data["street"] = data.get("StreetAddress")
    #             data["city"] = data.get("City")
    #             data["zip"] = data.get("Zip")
    #             data["email"] = data.get("Email")
    #             data["ContactType"] = str(data.get("ContactType"))
    #             data["name"] = data.get("FirstName") + data.get("LastName")
    #             data["customer"] = True
    #             data["FromParcelPro"] = True
    #             if data.get("State"):
    #                 state_rec = self.env['res.country.state'].search([('code', '=', data.get("State"))],limit=1)
    #                 if state_rec:
    #                     state_id = state_rec[0].id
    #                     country_id = state_rec.country_id and state_rec.country_id.id
    #             data["state_id"] = state_id
    #             data["country_id"] = country_id
    #             # data['login'] = data.get("Email") or data["name"]
    #             # data['login'] = data.get("UserId")
    #             data['login'] = data.get("ContactId")
    #             user = self.env['res.users'].create(data)
    #             return {"message": "Contact Successfully Created", "ContactId": data.get("ContactId"),"customer_id": user.partner_id.id}
    #         except ValidationError as e:
    #             raise ValidationError(_('There is something wrong ! %s ')%e.name)

    def get_contacts(self):
        session = self.get_session()
        if session:
                url = 'https://apibeta.parcelpro.com/v1/location?sessionID=' + session
                result = self.get_response(url, "GET",{})
        return result

    def get_contact(self, ContactId):
        if not ContactId:
            raise ValidationError(_('ContactId is required !'))
        session = self.get_session()
        if session:
            url = 'https://apibeta.parcelpro.com/v1/location/' + str(ContactId) + '?sessionID=' + session
            result = self.get_response(url, "GET",{})
        return result

    # Post Contact

    def post_contact(self,order,post_quotation):
        session = self.get_session()
        print("============",order.partner_id.phone)
        # data_dict_partner = {
        #     "ApartmentSuite": order.partner_id.ApartmentSuite or "",
        #     "City": order.partner_id.city or "",
        #     "CompanyName": "",
        #     "ContactId": "NOID",
        #     "Country": order.partner_id.Country or order.partner_id.country_id.code or "",
        #     "CustomerId": "",
        #     "Email": order.partner_id.email or "",
        #     "FaxNo": order.partner_id.FaxNo or "",
        #     "FirstName": order.partner_id.FirstName or "",
        #     "IsExpress": False,
        #     "IsResidential": True,
        #     "LastName": order.partner_id.LastName or "",
        #     "NickName": order.partner_id.NickName or "",
        #     "State": order.partner_id.State or order.partner_id.state_id.code or "",
        #     "StreetAddress": str(order.partner_id.street) + ',' + str(order.partner_id.street2),
        #     "TelephoneNo": order.partner_id.mobile or "",
        #     "Zip": order.partner_id.zip or ""
        # }

        data_dict_partner = {
            "ApartmentSuite": order.partner_id.ApartmentSuite,
            "City": order.partner_id.city,
            "CompanyName": "",
            "ContactId": "NOID",
            "Country": order.partner_id.Country or order.partner_id.country_id.code,
            "CustomerId": "",
            "Email": order.partner_id.email,
            "FaxNo": order.partner_id.FaxNo or "",
            "FirstName": order.partner_id.FirstName,
            "IsExpress": True,
            "IsResidential": False,
            "LastName": order.partner_id.LastName,
            "NickName": order.partner_id.NickName,
            "State": order.partner_id.State or order.partner_id.state_id.code,
            "StreetAddress": str(order.partner_id.street),
            "TelephoneNo": order.partner_id.mobile,
            "Zip": order.partner_id.zip
        }

        data_dict_shipping_partner = {
            "ApartmentSuite": order.partner_shipping_id.ApartmentSuite,
            "City": order.partner_shipping_id.city,
            "CompanyName": "",
            "ContactId": "NOID",
            "Country": order.partner_shipping_id.Country or order.partner_shipping_id.country_id.code,
            "CustomerId": "",
            "Email": order.partner_shipping_id.email,
            "FaxNo": order.partner_shipping_id.FaxNo or "",
            "FirstName": order.partner_shipping_id.FirstName,
            "IsExpress": True,
            "IsResidential": False,
            "LastName": order.partner_shipping_id.LastName,
            "NickName": order.partner_shipping_id.NickName,
            "State": order.partner_shipping_id.State or order.partner_shipping_id.state_id.code,
            "StreetAddress": str(order.partner_shipping_id.street),
            "TelephoneNo": order.partner_shipping_id.mobile,
            "Zip": order.partner_shipping_id.zip
        }
        url = 'https://apibeta.parcelpro.com/v1/location?sessionID=' + str(session)
        result = self.get_response(url, "POST", data_dict_partner)
        print("Final Result...........................",result,result.get("ContactId"))
        result_shipping = self.get_response(url, "POST", data_dict_shipping_partner)
        print("result_shipping........................",result_shipping,result_shipping.get("ContactId"))
        if not result.get("ContactId") or result.get("ContactId")=="NOID" or not result_shipping.get('ContactId') or result_shipping.get('ContactId')=="NOID":
            raise ValidationError(_('ContactId not created on Parcel Pro for custom or for shipping address'))
        order.partner_id.write({'CustomerId':result.get('CustomerId'),'ContactId':result.get('ContactId'),'ApartmentSuite':result.get('ApartmentSuite')})
        order.partner_shipping_id.write({'CustomerId':result_shipping.get('CustomerId'),'ContactId':result_shipping.get('ContactId'),'ApartmentSuite':result_shipping.get('ApartmentSuite')})
        if post_quotation:
            self.post_quotation(order,result.get("ContactId"),result_shipping.get('ContactId'))

    # Post Quotation

    def post_quotation(self,order):
        session = self.get_session()

        data_dict = {
                           "ShipmentId":"NOID",
                           "QuoteId":"",
                           "CustomerId":"NOID",
                           "UserId":"NOID",
                           "ShipToResidential":False,
                           "ServiceCode":"01-DOM",
                           "CarrierCode":2,
                           "ShipTo":{
                              "ContactId":"NOID",
                              "CustomerId":"",
                              "UserId":"",
                              "ContactType":11,
                              "CompanyName":"Test Company",
                              "FirstName":order.partner_shipping_id.FirstName,
                              "LastName":order.partner_shipping_id.LastName,
                              "StreetAddress":order.partner_shipping_id.street,
                              "ApartmentSuite":order.partner_shipping_id.ApartmentSuite or "",
                              "ProvinceRegion":"",
                              "City":order.partner_shipping_id.city,
                              "State":order.partner_shipping_id.State,
                              "Country":order.partner_shipping_id.Country,
                              "Zip":order.partner_shipping_id.zip,
                              "TelephoneNo":order.partner_shipping_id.mobile,
                              "FaxNo":order.partner_shipping_id.FaxNo or "",
                              "Email":order.partner_shipping_id.email or "",
                              "NickName":order.partner_shipping_id.NickName or "",
                              "IsExpress":False,
                              "IsResidential":False,
                              "IsUserDefault":False,
                              "UPSPickUpType":0,
                              "TotalContacts":"0"
                           },
                           "UpdateAddressBook":False,
                           "NotifyRecipient":False,
                           "ShipFrom":{
                              "ContactId":"NOID",
                              "CustomerId":"",
                              "UserId":"",
                              "ContactType":3,
                              "CompanyName":"Acme Jewelry",
                              "FirstName":order.partner_id.FirstName,
                              "LastName":order.partner_id.LastName,
                              "StreetAddress":order.partner_id.street,
                              "ApartmentSuite":order.partner_id.ApartmentSuite or "",
                              "ProvinceRegion":"",
                              "City":order.partner_id.city,
                              "State":order.partner_id.State,
                              "Country":order.partner_id.Country,
                              "Zip":order.partner_id.zip,
                              "TelephoneNo":order.partner_id.mobile,
                              "FaxNo":order.partner_id.FaxNo or "",
                              "Email":order.partner_id.email or "" ,
                              "NickName":order.partner_id.NickName or "",
                              "IsExpress":False,
                              "IsResidential":False,
                              "IsUserDefault":False,
                              "UPSPickUpType":0,
                              "TotalContacts":"0"
                           },
                           "ShipDate":"2019-05-30",
                           "PackageCode":"MEDIUM BOX",
                           "Height":0,
                           "Width":0,
                           "Length":0,
                           "Weight":10.0,
                           "InsuredValue":20.0,
                           "IsSaturdayPickUp":False,
                           "IsSaturdayDelivery":False,
                           "IsDeliveryConfirmation":False,
                           "IsCod":False,
                           "CodAmount":0.0,
                           "IsSecuredCod":False,
                           "IsRegularPickUp":False,
                           "IsDropoff":True,
                           "IsPickUpRequested":False,
                           "IsSmartPickUp":False,
                           "PickUpContactName":"",
                           "PickUpTelephone":"",
                           "PickUpAtHour":"",
                           "PickUpAtMinute":"",
                           "PickUpByHour":"",
                           "PickUpByMinute":"",
                           "PickUpDate":"",
                           "DispatchConfirmationNumber":"",
                           "DispatchLocation":"",
                           "NotifySender":False,
                           "ReferenceNumber":"",
                           "TrackingNumber":"",
                           "CustomerReferenceNumber":"",
                           "IsDirectSignature":False,
                           "IsThermal":True,
                           "IsMaxCoverageExceeded":False,
                           "Estimator":[
                           ],
                           "LabelImage":None,
                           "IsBillToThirdParty":False,
                           "BillToThirdPartyPostalCode":"",
                           "BillToAccount":"",
                           "IsShipFromRestrictedZip":False,
                           "IsShipToRestrictedZip":False,
                           "IsShipToHasRestrictedWords":False,
                           "IsShipFromHasRestrictedWords":False,
                           "IsHighValueShipment":False,
                           "IsHighValueReport":False,
                           "ReceivedBy":"",
                           "ReceivedTime":"",
                           "TotalShipments":"0"
                        }

        # data_dict["ShipFrom"]["ContactId"] = ContactId
        # data_dict["ShipTo"]["ContactId"] = ContactId_shipping
        # today_date = datetime.datetime.utcnow().date()
        # data_dict["ShipDate"] = str(today_date)
        if session:
            url = 'https://apibeta.parcelpro.com/v1/quote?sessionID=' + session
            result = self.get_response(url, "POST", data_dict)
            # param_data = json.dumps(data_dict)
            # headers = {"content-type": "application/json"}
            # response = requests.post(url, data=param_data, headers=headers)
            # result = json.loads(response.text)
            print("==result==============", result)
            print("Contact Id...", result["ShipFrom"]["ContactId"],result["ShipTo"]["ContactId"])
            if not result.get("QuoteId"):
                raise ValidationError(_('QuoteId not created on Parcel Pro '))
            print("***",result.get('IsHighValueShipment'))
            if result.get('IsHighValueShipment'):
                url = 'https://apibeta.parcelpro.com/v1/highvalue/' + result.get("QuoteId") + '?sessionID=' + session
                result = self.get_response(url, "POST", data_dict)
                print("== result  high value post ====",result)
            order.write({'QuoteId':result.get("QuoteId"),'IsHighValueShipment':result.get("IsHighValueShipment"),
                         'QuoteIdCreated':True,
                         'ServiceCode':result.get("ServiceCode"),
                         'PackageCode':result.get("PackageCode")})
            for estimator in result.get("Estimator"):
                estimator_rec = self.env['estimator'].create({'AccessorialsCost':estimator.get('AccessorialsCost'),
                                                        'BaseRate':estimator.get('BaseRate'),
                                                        'BusinessDaysInTransit':estimator.get('BusinessDaysInTransit'),
                                                        'DeliveryByTime':estimator.get('DeliveryByTime'),
                                                         'ExceededMaxCoverage':estimator.get('ExceededMaxCoverage'),
                                                         'EstimatorHeaderID':estimator.get('EstimatorHeaderID'),
                                                         'sale_order_id':order.id
                                                         })
                for detail in estimator.get('EstimatorDetail'):
                    self.env['estimator.detail'].create({'AccessorialsCost': detail.get('AccessorialsCost'),
                                                  'AccessorialFee': detail.get('AccessorialFee'),
                                                  'EstimatorDetailID': detail.get('EstimatorDetailID'),
                                                  'estimator_id': estimator_rec.id
                                                  })

                

        return result

    # Post Shipment

    def post_shipment(self, shipment):
        session = self.get_session()
        if session:
            url = 'https://apibeta.parcelpro.com/v1/shipment/' + str(shipment.QuoteId) + '?sessionID=' + session
            result = self.get_response(url, "POST", {})
            if not result.get("ShipmentID"):
                raise ValidationError(_('ShipmentID not created on Parcel Pro '))
            shipment.write({'ShipmentID': result.get("ShipmentID")})


    # Get Shipment

    def get_shipment(self,ShipmentID):
        if not ShipmentID:
            raise ValidationError(_('ShipmentID is required !'))
        session = self.get_session()
        if session:
            url = 'https://apibeta.parcelpro.com/v1/shipment/' + str(ShipmentID) + '?sessionID=' + session
            result = self.get_response(url, "GET",{})
        return result

    # Get Shipment Label

    def get_shipment_label(self, ShipmentID):
        if not ShipmentID:
            raise ValidationError(_('ShipmentID is required !'))
        session = self.get_session()
        if session:
            url = 'https://apibeta.parcelpro.com/v1/shipment/label?shipmentId=' + str(ShipmentID) + '&sessionID=' + session
            print("====", url)
            result = self.get_response(url, "GET",{})
            print("result", result)
        return result

    # High Value Queue

    def get_high_value_queue(self,QuoteId):
        if not QuoteId:
            raise ValidationError(_('QuoteId is required !'))
        session = self.get_session()
        if session:
            url = 'https://apibeta.parcelpro.com/v1/highvalue/' + str(QuoteId) + '?sessionID=' + session
            result = self.get_response(url, "GET",{})
            if result.get('Status') == 0:
                result['state'] = 'New'
            elif result.get('Status') == 1:
                result['state'] = 'Assigned'
            elif result.get('Status') == 2:
                result['state'] = 'Approved'
            elif result.get('Status') == 3:
                result['state'] = 'Rejected'
            elif result.get('Status') == 4:
                result['state'] = 'Printed'
            elif result.get('Status') == 5:
                result['state'] = 'Expired'
            elif result.get('Status') == 6:
                result['state'] = 'Voided'
            elif result.get('Status') == 7:
                result['state'] = 'Cancelled'
            else:
                result['state'] = 'None'
            print("result", result)
        return result


    # Get carrier services

    def get_carrier_services(self,domesticonly,carriercode):
        session = self.get_session()
        # https: // apibeta.parcelpro.com / v1 / carrierservices?domesticonly = True & carriercode = UPS & sessionID = vp5kcsyrcvhxc1ruifho2m0c
        if session:
            url = 'https://apibeta.parcelpro.com/v1/carrierservices?domesticonly=' + str(domesticonly) + '&carriercode='+ str(carriercode) + '&sessionID=' + session
            print("====", url)
            result = self.get_response(url, "GET", {})
            print("result", result)
        return result

    # Get package types

    def get_package_types(self,carrierservicecode,carriercode):
        session = self.get_session()
        if session:
            url = 'https://apibeta.parcelpro.com/v1/packagetypes?carrierservicecode=' + str(carrierservicecode) + '&carriercode='+ str(carriercode) + '&sessionID=' + session
            print("====", url)
            result = self.get_response(url, "GET", {})
            print("result", result)
        return result

    # ZIP Code Validator

    def get_zip_code_validator(self,zipcode):
        session = self.get_session()
        if session:
            # https://apibeta.parcelpro.com/v1/zipcodevalidator?zipcode=90501&sessionID=cbkrzrwnbbzuqbrmsgeifrgg
            url = 'https://apibeta.parcelpro.com/v1/zipcodevalidator?zipcode=' + str(zipcode)  + '&sessionID=' + session
            print("====", url)
            result = self.get_response(url, "GET", {})
            print("result", result)
        return result