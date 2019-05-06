# -*- coding: utf-8 -*-

from odoo.http import Controller, request, route

from ..tools import make_response, eval_request_params
from odoo.exceptions import ValidationError
import requests
import json

class RestApi(Controller):

    @route('/api/auth', auth='public', methods=["POST"], csrf=False)
    @make_response()
    def authenticate(self, db, login, password):
        request.session.authenticate(db, login, password)
        return request.env['ir.http'].session_info()

    def get_response(self,url,type):
        print("===",url)
        headers = {"content-type": "application/json"}
        response = requests.request(type, url, headers=headers)
        print("==response=",response)
        print("===")
        result = json.loads(response.text)
        return result


    @route('/api/generatesession', auth='public', methods=["POST"], csrf=False)
    @make_response()
    def generate_session(self,  **kwargs):
        print("========",kwargs)
        eval_request_params(kwargs)
        parcel_config_rec = request.env['parcel.configuration'].sudo().search([])
        result = {}
        if parcel_config_rec:
            result['user_name'] = parcel_config_rec[0].user_name
            result['password'] = parcel_config_rec[0].password
            result['api_key'] = parcel_config_rec[0].api_key
            try:
                url = 'https://apibeta.parcelpro.com/v1/auth?username=' + parcel_config_rec[0].user_name + '&password=' + parcel_config_rec[0].password + '&apikey=' + parcel_config_rec[0].api_key
                result = self.get_response(url,"GET")
                if result.get('SessionID'):
                    parcel_config_rec['session'] = result.get('SessionID')
                    result["remark"] = "This session Id is updated in Odoo Configuration"
            except ValidationError as e:
                self.assertEqual(e.name, self.model_obj._get_error_message())
                result = {'message': "There is something wrong !", 'reason': e.name}
        else:
            result = {"status": "failed", "message": "There is no configuration found for API !"}
        return result

    def get_session(self):
        parcel_config_rec = request.env['parcel.configuration'].search([])
        result = {}
        if parcel_config_rec:
            result['session'] = parcel_config_rec[0].session
        return result

    @route('/api/getgeneratemulticontacts', auth='public', methods=["POST"], csrf=False)
    @make_response()
    def get_contacts(self,**kwargs):
        eval_request_params(kwargs)
        data = self.get_session()
        session = data.get('session')
        if session:
            try:
                url = 'https://apibeta.parcelpro.com/v1/location?sessionID=' + session
                result = self.get_response(url,"GET")
                if kwargs.get('create_contact') == 'true':
                    lst = []
                    for d in result:
                        customer_rec = request.env['res.partner'].search([('ContactId', '=', d.get("ContactId"))],limit=1)
                        if customer_rec:
                            lst.append({"message": "Contact Already Exist", "ContactId": d.get("ContactId"),
                                        })
                            continue
                        state_id = False
                        country_id = False
                        d["mobile"] = d.get("TelephoneNo")
                        d["fax"] = d.get("FaxNo")
                        d["street"] = d.get("StreetAddress")
                        d["city"] = d.get("City")
                        d["zip"] = d.get("Zip")
                        d["name"] = d.get("FirstName") + d.get("LastName")
                        d["customer"] = True
                        if d.get("State"):
                            state_rec = request.env['res.country.state'].search([('code', '=', d.get("State"))],limit=1)
                            if state_rec:
                                state_id = state_rec[0].id
                                country_id = state_rec.country_id and state_rec.country_id.id
                        d["state_id"] = state_id
                        d["country_id"] = country_id
                        d["FromParcelPro"] = True
                        prtner_rec= request.env['res.partner'].create(d)
                        lst.append({"message":"Contact Successfully Created","ContactId":d.get("ContactId"),"customer_id":prtner_rec.id})
                    return lst
            except ValidationError as e:
                self.assertEqual(e.name, self.model_obj._get_error_message())
                result = {'message': "There is something wrong !", 'reason': e.name}
        else:
            result = {"status": "failed", "message": "There is no session found for API in Configuraton !"}
        return result

    @route('/api/getgeneratecontact', auth='public', methods=["POST"], csrf=False)
    @make_response()
    def generate_contact(self, **kwargs):
        eval_request_params(kwargs)
        if not kwargs.get('ContactId'):
            result = {"status": "failed", "message": "ContactId parameter is missing !"}
            return result
        data = self.get_session()
        session = data.get('session')
        if session:
            try:
                url = 'https://apibeta.parcelpro.com/v1/location/' + str(kwargs.get('ContactId')) +'?sessionID=' + session
                result  = self.get_response(url,"GET")
                print("result",result)
                if kwargs.get('create_contact') == 'true':
                    customer_rec = request.env['res.partner'].search([('ContactId', '=', result.get("ContactId"))],
                                                                     limit=1)
                    if customer_rec:
                        return {"message": "Contact Already Exist", "ContactId": result.get("ContactId")}
                    state_id = False
                    country_id = False
                    result["mobile"] = result.get("TelephoneNo")
                    result["fax"] = result.get("FaxNo")
                    result["street"] = result.get("StreetAddress")
                    result["city"] = result.get("City")
                    result["zip"] = result.get("Zip")
                    result["name"] = result.get("FirstName") + result.get("LastName")
                    result["customer"] = True
                    result["FromParcelPro"] = True
                    if result.get("State"):
                        state_rec = request.env['res.country.state'].search([('code', '=', result.get("State"))],
                                                                            limit=1)
                        if state_rec:
                            state_id = state_rec[0].id
                            country_id = state_rec.country_id and state_rec.country_id.id
                    result["state_id"] = state_id
                    result["country_id"] = country_id
                    prtner_rec = request.env['res.partner'].create(result)
                    result = {"message": "Contact Successfully Created", "ContactId": result.get("ContactId"),
                                "customer_id": prtner_rec.id}
            except ValidationError as e:
                self.assertEqual(e.name, self.model_obj._get_error_message())
                result = {'message': "There is something wrong !", 'reason': e.name}
        else:
            result = {"status": "failed", "message": "There is no session found for API in Configuraton !"}
        return result

    @route('/api/getgeneratequotation', auth='public', methods=["POST"], csrf=False)
    @make_response()
    def generate_quotation(self, **kwargs):
        eval_request_params(kwargs)
        print("======kwargs====",type(kwargs))
        # kwargs = sorted(kwargs.keys())
        data = self.get_session()
        session = data.get('session')
        if session:
            false = False
            true = True
            null = None
            try:
                param_data = {
                    "ShipmentId": "NOID",
                    "QuoteId": "",
                    "CustomerId": "NOID",
                    "UserId": "NOID",
                    "ShipToResidential": false,
                    "ServiceCode": "01-DOM",
                    "CarrierCode": 2,
                    "ShipTo": {
                        "ContactId": "NOID",
                        "CustomerId": "",
                        "UserId": "",
                        "ContactType": 11,
                        "CompanyName": "Test Company",
                        "FirstName": "Matt",
                        "LastName": "Jones",
                        "StreetAddress": "1101 Beach Blvd",
                        "ApartmentSuite": "",
                        "ProvinceRegion": "",
                        "City": "LA PALMA",
                        "State": "CA",
                        "Country": "US",
                        "Zip": "90623",
                        "TelephoneNo": "7145551212",
                        "FaxNo": "",
                        "Email": "",
                        "NickName": "",
                        "IsExpress": false,
                        "IsResidential": false,
                        "IsUserDefault": false,
                        "UPSPickUpType": 0,
                        "TotalContacts": "0"
                    },
                    "UpdateAddressBook": false,
                    "NotifyRecipient": false,
                    "ShipFrom": {
                        "ContactId": "NOID",
                        "CustomerId": "",
                        "UserId": "",
                        "ContactType": 3,
                        "CompanyName": "Acme Jewelry",
                        "FirstName": "DDDDDDDDDDDDDDDD",
                        "LastName": "N72",
                        "StreetAddress": "10011 Holmgren Road",
                        "ApartmentSuite": "",
                        "ProvinceRegion": "",
                        "City": "ONEIDA",
                        "State": "WI",
                        "Country": "US",
                        "Zip": "54155",
                        "TelephoneNo": "9205551212",
                        "FaxNo": "",
                        "Email": "",
                        "NickName": "Dikuuuuuuuuuuuuuuuuu",
                        "IsExpress": false,
                        "IsResidential": false,
                        "IsUserDefault": false,
                        "UPSPickUpType": 0,
                        "TotalContacts": "0"
                    },
                    "ShipDate": "2019-05-30",
                    "PackageCode": "MEDIUM BOX",
                    "Height": 0,
                    "Width": 0,
                    "Length": 0,
                    "Weight": 10.0,
                    "InsuredValue": 20.0,
                    "IsSaturdayPickUp": false,
                    "IsSaturdayDelivery": false,
                    "IsDeliveryConfirmation": false,
                    "IsCod": false,
                    "CodAmount": 0.0,
                    "IsSecuredCod": false,
                    "IsRegularPickUp": false,
                    "IsDropoff": true,
                    "IsPickUpRequested": false,
                    "IsSmartPickUp": false,
                    "PickUpContactName": "",
                    "PickUpTelephone": "",
                    "PickUpAtHour": "",
                    "PickUpAtMinute": "",
                    "PickUpByHour": "",
                    "PickUpByMinute": "",
                    "PickUpDate": "",
                    "DispatchConfirmationNumber": "",
                    "DispatchLocation": "",
                    "NotifySender": false,
                    "ReferenceNumber": "",
                    "TrackingNumber": "",
                    "CustomerReferenceNumber": "",
                    "IsDirectSignature": false,
                    "IsThermal": true,
                    "IsMaxCoverageExceeded": false,
                    "Estimator": [  ],
                    "LabelImage": null,
                    "IsBillToThirdParty": false,
                    "BillToThirdPartyPostalCode": "",
                    "BillToAccount": "",
                    "IsShipFromRestrictedZip": false,
                    "IsShipToRestrictedZip": false,
                    "IsShipToHasRestrictedWords": false,
                    "IsShipFromHasRestrictedWords": false,
                    "IsHighValueShipment": false,
                    "IsHighValueReport": false,
                    "ReceivedBy": "",
                    "ReceivedTime": "",
                    "TotalShipments": "0"
                }
                url = 'https://apibeta.parcelpro.com/v1/quote?sessionID=' + session
                param_data = json.dumps(kwargs)
                headers = {"content-type": "application/json"}
                response = requests.post(url, data=param_data, headers=headers)
                result = json.loads(response.text)
                print("==result=",result)
                if kwargs.get('create_quotation') == 'true':
                    if result.get("QuoteId"):
                        quote_rec = request.env['sale.order'].search([('QuoteId', '=', result.get("QuoteId"))])
                        if quote_rec:
                            return {"message": "Quotation Already Exist", "QuoteId": result.get("QuoteId")}
                        partner_id = False
                        country_id = False
                        if result.get("ContactId"):
                            contact_rec = request.env['res.partner'].search([('ContactId', '=', result.get("ContactId"))])
                            if contact_rec:
                                partner_id = contact_rec[0].id
                        elif result.get("Email"):
                            prtner_rec = request.env['res.partner'].create(result)
                        print("====",)
                        prtner_rec = request.env['sale.order'].create(result)
                        result = {"message": "Quotation Successfully Created", "ContactId": result.get("ContactId"),
                              "customer_id": prtner_rec.id}
                    else:
                        result = {"message": "QuoteId not created on Pro Parcel."}

            except ValidationError as e:
                self.assertEqual(e.name, self.model_obj._get_error_message())
                result = {'message': "There is something wrong !", 'reason': e.name}
        else:
            result = {"status": "failed", "message": "There is no session found for API in Configuraton !"}
        return result










