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

    def get_response(self, url,type):
        print("===", url)
        headers = {"content-type": "application/json"}
        response = requests.request(type, url, headers=headers)
        result = json.loads(response.text)
        return result

    def generate_session(self):
        parcel_config_rec = self.search([])
        result = {}
        if parcel_config_rec:
            result['user_name'] = parcel_config_rec[0].user_name
            result['password'] = parcel_config_rec[0].password
            result['api_key'] = parcel_config_rec[0].api_key
            try:
                url = 'https://apibeta.parcelpro.com/v1/auth?username=' + parcel_config_rec[0].user_name + '&password=' + parcel_config_rec[0].password + '&apikey=' + parcel_config_rec[0].api_key
                result = self.get_response(url, "GET")
                print("======", result.get('SessionID'))
                if result.get('SessionID'):
                    parcel_config_rec.write({'session':result.get('SessionID')})
                    result["remark"] = "This session Id is updated in Odoo Configuration"
            except ValidationError as e:
                
                raise ValidationError(_('There is something wrong ! %s ')%e.name)
        else:
            raise ValidationError(_('There is no configuration found for API !'))
        return result

    def get_session(self):
        parcel_config_rec = self.search([],limit=1)
        if parcel_config_rec and parcel_config_rec[0].session:
            return parcel_config_rec[0].session
        else:
            raise ValidationError(_('There is no session found for API in Configuration '))

    def create_contact(self,data):
        state_id = False
        country_id = False
        customer_rec = self.env['res.partner'].search([('ContactId', '=', data.get('ContactId'))], limit=1)
        if customer_rec:
            return {"message": "Contact Already Exist", "ContactId": data.get('ContactId')}
        else:
            try:
                data["mobile"] = data.get("TelephoneNo")
                data["fax"] = data.get("FaxNo")
                data["street"] = data.get("StreetAddress")
                data["city"] = data.get("City")
                data["zip"] = data.get("Zip")
                data["email"] = data.get("Email")
                data["ContactType"] = str(data.get("ContactType"))
                data["name"] = data.get("FirstName") + data.get("LastName")
                data["customer"] = True
                data["FromParcelPro"] = True
                if data.get("State"):
                    state_rec = self.env['res.country.state'].search([('code', '=', data.get("State"))],limit=1)
                    if state_rec:
                        state_id = state_rec[0].id
                        country_id = state_rec.country_id and state_rec.country_id.id
                data["state_id"] = state_id
                data["country_id"] = country_id
                # data['login'] = data.get("Email") or data["name"]
                # data['login'] = data.get("UserId")
                data['login'] = data.get("ContactId")
                user = self.env['res.users'].create(data)
                return {"message": "Contact Successfully Created", "ContactId": data.get("ContactId"),"customer_id": user.partner_id.id}
            except ValidationError as e:
                
                raise ValidationError(_('There is something wrong ! %s ')%e.name)

    def get_contacts(self,create_contact):
        result = {}
        session = self.get_session()
        if session:
            try:
                url = 'https://apibeta.parcelpro.com/v1/location?sessionID=' + session
                result = self.get_response(url, "GET")
                print("Response from parcel pro..",result)
                if create_contact:
                    lst = []
                    for d in result:
                        result  = self.create_contact(d)
                        lst.append(result)
                    return lst
            except ValidationError as e:
                
                raise ValidationError(_('There is something wrong ! %s ')%e.name)
        return result

    def get_contact(self, ContactId,create_contact):
        result = {}
        if not ContactId:
            raise ValidationError(_('ContactId is required !'))
        session = self.get_session()
        if session:
            try:
                url = 'https://apibeta.parcelpro.com/v1/location/' + str(ContactId) + '?sessionID=' + session
                result = self.get_response(url, "GET")
                print("result", result)
                if create_contact:
                    result = self.create_contact(result)
            except ValidationError as e:
                
                raise ValidationError(_('There is something wrong ! %s ')%e.name)
        return result

    # Post Quotation

    def generate_quotation(self,sale_rec):
        session = self.get_session()
        null = None
        false = False
        true = True
        data_dict =  {
                       "ShipmentId":"NOID",
                       "QuoteId":"",
                       "CustomerId":"NOID",
                       "UserId":"NOID",
                       "ShipToResidential":false,
                       "ServiceCode":"01-DOM",
                       "CarrierCode":2,
                       "ShipTo":{
                          "ContactId":"NOID",
                       },
                       "UpdateAddressBook":false,
                       "NotifyRecipient":false,
                       "ShipFrom":{
                          "ContactId":"NOID",
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
                       "CodAmount":30,
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
        data_dict["ShipFrom"]["ContactId"] = sale_rec.partner_id.ContactId
        data_dict["ShipTo"]["ContactId"] = sale_rec.partner_shipping_id.ContactId
        today_date = datetime.datetime.utcnow().date()
        data_dict["ShipDate"] = str(today_date)
        print("==data_dict==",data_dict)

        if session:
            try:
                url = 'https://apibeta.parcelpro.com/v1/quote?sessionID=' + session
                param_data = json.dumps(data_dict)
                headers = {"content-type": "application/json"}
                response = requests.post(url, data=param_data, headers=headers)
                result = json.loads(response.text)
                print("==result=#", result)
                if result.get("QuoteId"):
                    sale_rec.write({'QuoteId':result.get("QuoteId")})
                else:
                    raise ValidationError(_('QuoteId not create on Parcel Pro '))
            except ValidationError as e:
                raise ValidationError(_('Warning ! %s ') % e.name)
        return result


    # Get Shipment

    def get_shipment(self,ShipmentID):
        result = {}
        if not ShipmentID:
            raise ValidationError(_('ShipmentID is required !'))
        session = self.get_session()
        if session:
            try:
                url = 'https://apibeta.parcelpro.com/v1/shipment/' + str(ShipmentID) + '?sessionID=' + session
                result = self.get_response(url, "GET")
            except ValidationError as e:
                
                result = {'status': "failed", 'reason': e.name}
        return result

    # Get Shipment Label

    def get_shipment_label(self, ShipmentID):
        result = {}
        if not ShipmentID:
            raise ValidationError(_('ShipmentID is required !'))
        session = self.get_session()
        if session:
            try:
                url = 'https://apibeta.parcelpro.com/v1/shipment/label?shipmentId=' + str(ShipmentID) + '&sessionID=' + session
                print("====", url)
                result = self.get_response(url, "GET")
                print("result", result)
            except ValidationError as e:
                
                result = {'status': "failed", 'reason': e.name}
        return result

    # High Value Queue

    def get_high_value_queue(self,QuoteId):
        result = {}
        if not QuoteId:
            raise ValidationError(_('QuoteId is required !'))
        session = self.get_session()
        if session:
            try:
                url = 'https://apibeta.parcelpro.com/v1/highvalue/' + str(QuoteId) + '?sessionID=' + session
                result = self.get_response(url, "GET")
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
            except ValidationError as e:
                
                result = {'status': "failed", 'reason': e.name}
        return result