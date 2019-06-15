# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from odoo.exceptions import ValidationError
import requests
import json
import datetime
from datetime import date
import base64

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
            headers = {"content-type": "application/json"}
            if type=="GET":
                response = requests.request(type, url, headers=headers)
            elif type =="POST":
                param_data = json.dumps(data_dict)
                print("Parameters in convert json.......",param_data)
                print("url..",url)
                print("===headers======",headers)
                response = requests.post(url, data=param_data, headers=headers)
            print("===",response.status_code)
            if response.status_code in ( 201,200):
                print("6666444444444")
                result = json.loads(response.text)
        except ValidationError as e:
            raise ValidationError(_('There is something wrong ! %s ') % e)
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

    def post_contact(self,partner):
        session = self.get_session()
        print("============",partner.name)
        data_dict_partner = {
            "ApartmentSuite": partner.ApartmentSuite,
            "City": partner.city,
            "CompanyName": partner.company_id.name,
            "ContactId": partner.ContactId or "NOID" ,
            "Country": partner.Country,
            "CustomerId": "",
            "Email": partner.email,
            "FaxNo": partner.FaxNo or "",
            "FirstName": partner.FirstName,
            "IsExpress": partner.IsExpress,
            "IsResidential": partner.IsResidential,
            "LastName": partner.LastName,
            "NickName": partner.NickName,
            "State": partner.State,
            "StreetAddress": str(partner.street),
            "TelephoneNo": partner.mobile,
            "Zip": partner.zip,
            "ContactType":partner.ContactType
        }
        print("++++++",partner.ContactType,type(partner.ContactType))
        if not partner.ContactType or ( partner.ContactType != '3' and partner.ContactType != '11' ):
            raise ValidationError(_('Contact Type should be selected as Location or Addressbook'))
        url = 'https://apibeta.parcelpro.com/v1/location?sessionID=' + str(session)
        if partner.ContactType == '3':
            url = 'https://apibeta.parcelpro.com/v1/location?sessionID=' + str(session)
        elif partner.ContactType == '11':
            data_dict_partner["UserId"]=partner.UserId
            # if partner.ContactId:
            #     data_dict_partner["ContactId"] = partner.ContactId
            #     url = 'https://apibeta.parcelpro.com/v1/addressbook/'+ str(data_dict_partner["ContactId"])  +'?sessionID=' + str(session)
            # else:
            url = 'https://apibeta.parcelpro.com/v1/addressbook?sessionID=' + str(session)
        result = self.get_response(url, "POST", data_dict_partner)
        print("result..............",result)
        if not result.get("ContactId") or result.get("ContactId")=="NOID" :
            raise ValidationError(_('ContactId not created on Parcel Pro'))
        if result.get('ApartmentSuite')=='false':
            ApartmentSuite = ""
        else:
            ApartmentSuite = result.get('ApartmentSuite')
        partner.write({'contact_created':True,'CustomerId':result.get('CustomerId'),'ContactId':result.get('ContactId'),'ApartmentSuite':ApartmentSuite,"Message":"Created/Updated Successfully"})
        return result


    # Post Quotation

    def post_quotation(self,order):
        p_excep = self.env['parcel.pro.exceptions']
        ShipDate = order.ShipDate
        current_date = date.today().strftime("%Y-%m-%d")

        if order.PickUpDate and order.PickUpDate > order.ShipDate:
            p_excep.create({'name':order.name,'api_type':'post_quotation','message':"Ship Date is less than Pick Up date."})
            raise ValidationError(_('Ship Date should be greater than pickUp date.'))
        if ShipDate < current_date:
            p_excep.create({'name': order.name, 'api_type': 'post_quotation', 'message': "ShipDate should be greater than Current Date !"})
            raise ValidationError(_('ShipDate should be greater than Current Date !'))
        if order.partner_id.id == order.partner_shipping_id.id:
            p_excep.create({'name': order.name, 'api_type': 'post_quotation', 'message': "Ship From and Ship To should be different location"})
            raise ValidationError(_('Ship From and Ship To should be different location.'))
        if order.Weight <= 0:
            p_excep.create({'name': order.name, 'api_type': 'post_quotation','message': "Weight should be greater than 0"})
            raise ValidationError(_('Weight should be greater than 0'))
        session = self.get_session()
        CodAmount = 0
        if order.IsCod:
            CodAmount = order.amount_total
        InsuredValue = 0
        for line in order.order_line:
            if line.product_id.type=='service' :
                InsuredValue = line.price_unit
                break
        # if InsuredValue <= 0:
        #     raise ValidationError(_('InsuredValue should be greater than 0'))



        print("=========",order.partner_id.ContactId)
        if not order.partner_id.ContactId:
            raise ValidationError(_('ShipFrom ContactId not Found ! '))
        if not order.partner_shipping_id.ContactId:
            raise ValidationError(_('ShipTo ContactId not not Found ! '))
        data_dict = {
                    "ShipmentId":"NOID",
                    "QuoteId":"",
                    "CustomerId":"NOID",
                    "UserId":0,
                    "ShipToResidential":order.ShipToResidential,
                    "ServiceCode":str(order.ServiceCode.name),
                    "CarrierCode":int(order.CarrierCode),
                    "ShipTo": {
                      "ContactId":order.partner_shipping_id.ContactId or "NOID",
                      # "CustomerId":"",
                      # "UserId":"",
                      # "ContactType":order.partner_shipping_id.ContactType,
                      # "CompanyName":order.company_id.name,
                      # "FirstName":order.partner_shipping_id.FirstName,
                      # "LastName":order.partner_shipping_id.LastName,
                      # "StreetAddress":order.partner_shipping_id.street,
                      # "ApartmentSuite":order.partner_shipping_id.ApartmentSuite or "",
                      # "ProvinceRegion":order.partner_shipping_id.ProvinceRegion,
                      # "City":order.partner_shipping_id.city,
                      # "State":order.partner_shipping_id.State,
                      # "Country":order.partner_shipping_id.Country,
                      # "Zip":order.partner_shipping_id.zip,
                      # "TelephoneNo":order.partner_shipping_id.mobile,
                      # "FaxNo":order.partner_shipping_id.FaxNo or "",
                      # "Email":order.partner_shipping_id.email or "",
                      # "NickName":order.partner_shipping_id.NickName or "",
                      # "IsExpress":order.partner_shipping_id.IsExpress,
                      # "IsResidential":order.partner_shipping_id.IsResidential,
                      # "IsUserDefault":order.partner_shipping_id.IsUserDefault,
                      # "UPSPickUpType":order.partner_shipping_id.UPSPickUpType,

                      # "TotalContacts":"0"
                    },
                    "UpdateAddressBook":order.UpdateAddressBook,
                    "NotifyRecipient":order.NotifyRecipient,
                    "ShipFrom":{
                              "ContactId":order.partner_id.ContactId or "NOID",
                              # "CustomerId":"",
                              # "UserId":"",
                              # "ContactType":order.partner_id.ContactType,
                              # "CompanyName":order.company_id.name,
                              # "FirstName":order.partner_id.FirstName,
                              # "LastName":order.partner_id.LastName,
                              # "StreetAddress":order.partner_id.street,
                              # "ApartmentSuite":order.partner_id.ApartmentSuite or "",
                              # "ProvinceRegion":order.partner_id.ProvinceRegion,
                              # "City":order.partner_id.city,
                              # "State":order.partner_id.State,
                              # "Country":order.partner_id.Country,
                              # "Zip":order.partner_id.zip,
                              # "TelephoneNo":order.partner_id.mobile,
                              # "FaxNo":order.partner_id.FaxNo or "",
                              # "Email":order.partner_id.email or "" ,
                              # "NickName":order.partner_id.NickName or "",
                              # "IsExpress":order.partner_id.IsExpress,
                              # "IsResidential":order.partner_id.IsResidential,
                              # "IsUserDefault":order.partner_id.IsUserDefault,
                              # "UPSPickUpType":order.partner_id.UPSPickUpType,
                              # "TotalContacts":"0"
                    },
                    "ShipDate":ShipDate,
                    "PackageCode":str(order.PackageCode.name),
                    "Height":float(order.Height) or 0,
                    "Width":float(order.Width) or 0,
                    "Length":float(order.Length) or 0,
                    "Weight":float(order.Weight) or 0,
                    "InsuredValue":InsuredValue or 0,
                    "InsuredValueThreshold":order.InsuredValueThreshold or "0",
                    "InsuredValueMultiplier":order.InsuredValueMultiplier or "0",
                    "IsSaturdayPickUp":order.IsSaturdayPickUp,
                    "IsSaturdayDelivery":order.IsSaturdayDelivery,
                    "IsDeliveryConfirmation":order.IsDeliveryConfirmation,
                    "IsCod":order.IsCod,
                    "CodAmount":CodAmount,
                    "IsSecuredCod":order.IsSecuredCod,
                    "IsRegularPickUp":order.IsRegularPickUp,
                    "IsDropoff":order.IsDropoff,
                    "IsPickUpRequested":order.IsPickUpRequested,
                    "IsSmartPickUp":order.IsSmartPickUp,
                    "PickUpContactName":str(order.PickUpContactName) or "",
                    "PickUpTelephone":order.PickUpTelephone or "",
                    "PickUpAtHour":order.PickUpAtMinute or "",
                    "PickUpAtMinute":order.PickUpAtMinute or "",
                    "PickUpByHour":order.PickUpByHour or "",
                    "PickUpByMinute":order.PickUpByMinute or "",
                    "PickUpDate": order.PickUpDate,
                    "DispatchConfirmationNumber":order.DispatchConfirmationNumber or "",
                    "DispatchLocation":order.DispatchLocation,
                    "NotifySender":order.NotifySender,
                    "ReferenceNumber":order.ReferenceNumber,
                    "TrackingNumber":"",
                    "CustomerReferenceNumber":order.CustomerReferenceNumber,
                    "IsDirectSignature":order.IsDirectSignature,
                    "IsThermal":order.IsThermal,
                    "IsMaxCoverageExceeded":order.IsMaxCoverageExceeded,
                    "Estimator":[],
                    "LabelImage":None,
                    "IsBillToThirdParty":order.IsBillToThirdParty,
                    "BillToThirdPartyPostalCode":order.BillToThirdPartyPostalCode or "",
                    "BillToAccount":order.BillToAccount,
                    "IsShipFromRestrictedZip":order.IsShipFromRestrictedZip,
                    "IsShipToRestrictedZip":order.IsShipToRestrictedZip,
                    "IsShipToHasRestrictedWords":order.IsShipFromHasRestrictedWords,
                    "IsShipFromHasRestrictedWords":False,
                    "IsHighValueShipment":False,
                    "IsHighValueReport":False,
                    "ReceivedBy":"",
                    "ReceivedTime":"",
                    "TotalShipments":"0"
                    }
        if session:
            IsHighValueShipment = False
            IsHighValueShipmentPosted = False
            url = 'https://apibeta.parcelpro.com/v1/quote?sessionID=' + session
            result = self.get_response(url, "POST", data_dict)
            # if not result.get("ShipFrom").get("ContactId") or result.get("ShipFrom").get("ContactId")=="NOID" :
            #     raise ValidationError(_('ShipFrom ContactId not created on Parcel Pro '))
            # if not result.get("ShipTo").get("ContactId") or result.get("ShipTo").get("ContactId")=="NOID":
            #     raise ValidationError(_('ShipTo ContactId not created on Parcel Pro '))
            if not result.get("QuoteId"):
                raise ValidationError(_('QuoteId not created on Parcel Pro '))
            if result.get('IsHighValueShipment'):
                url = 'https://apibeta.parcelpro.com/v1/highvalue/' + result.get("QuoteId") + '?sessionID=' + session
                self.get_response(url, "POST", {})
                IsHighValueShipment = True
                IsHighValueShipmentPosted = True

            total_shipping_charges = 0.00
            for estimator in result.get("Estimator"):
                total_shipping_charges += estimator.get('TotalCharges')
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
                                                  'estimator_id': estimator_rec.id})
            if total_shipping_charges > 0:
                order._create_delivery_line(order.carrier_id, total_shipping_charges)

            order.write({'QuoteId': result.get("QuoteId"),
                         'QuoteIdCreated': True,
                         'IsHighValueShipment': IsHighValueShipment,
                         'IsHighValueShipmentPosted': IsHighValueShipmentPosted
                         })

        return result

    # Post Shipment

    def post_shipment(self, shipment):
        session = self.get_session()
        if session:
            data_dict = {}
            url = 'https://apibeta.parcelpro.com/v1/shipment/' + str(shipment.QuoteId) + '?sessionID=' + session
            result = self.get_response(url, "POST", data_dict)
            if not result.get("ShipmentId") or result.get("ShipmentId") == "NOID":
                raise ValidationError(_('ShipmentID not created on Parcel Pro '))
            LabelImage = self.get_shipment(result.get("ShipmentId"))
            shipment.write({'ShipmentId': result.get("ShipmentId"),'carrier_tracking_ref': result.get("TrackingNumber")})
            name = "Shipping Label" + result.get("ShipmentId")
            self.env['ir.attachment'].create(
                {'res_model': "stock.picking", 'datas_fname': name, 'name':name  ,'datas': LabelImage.encode(),
                 'res_id': shipment.id})


    # Get Shipment

    def get_shipment(self,ShipmentID):
        if not ShipmentID:
            raise ValidationError(_('ShipmentID is required !'))
        session = self.get_session()
        if session:
            url = 'https://apibeta.parcelpro.com/v1/shipment/' + str(ShipmentID) + '?sessionID=' + session
            print("url......",url)
            try:
                headers = {"content-type": "application/xml"}
                response = requests.request("GET", url, headers=headers)
                result = response.text
                from xml.etree.ElementTree import XML
                LabelImage = XML(result).find("LabelImage").text
            except ValidationError as e:
                raise ValidationError(_('There is something wrong ! %s ') % e)
        return LabelImage

    # Get Shipment Label

    def get_shipment_label(self, ShipmentId):
        if not ShipmentId:
            raise ValidationError(_('ShipmentId is required !'))
        session = self.get_session()
        if session:
            data_dict = {}
            url = 'https://apibeta.parcelpro.com/v1/shipment/label?shipmentId=' + str(ShipmentId) + '&sessionID=' + session
            print("====", url)

            try:
                headers = {"content-type": "application/xml"}
                response = requests.request("GET", url, headers=headers)
                result = response.text
                # from xml.etree.ElementTree import XML
                # LabelImage = XML(result).find("LabelImage").text
            except ValidationError as e:
                raise ValidationError(_('There is something wrong ! %s ') % e)

            #
            # result = self.get_response(url, "GET",data_dict)
            # print("result", result)
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
        if session:
            url = 'https://apibeta.parcelpro.com/v1/carrierservices?domesticonly=' + str(domesticonly) + '&carriercode='+ str(carriercode) + '&sessionID=' + session
            print("====", url)
            result = self.get_response(url, "GET", {})
            print("result", result)
            carrier_service_rec = self.env["carrier.services"]
            for r in result:
                print("======",r)
                print("========",r.get('CarrierCode'))
                carrier_service_id = carrier_service_rec.search([('name','=',r.get('ServiceCode')),('CarrierCode','=',r.get('CarrierCode'))])
                if not carrier_service_id:
                    r['name'] = r.get('ServiceCode')
                    r['CarrierCode'] = str(r['CarrierCode'])
                    carrier_service_rec.create(r)
        return result

    # Get package types

    def get_package_types(self,carrierservicecode,carriercode):
        session = self.get_session()
        if session:
            url = 'https://apibeta.parcelpro.com/v1/packagetypes?carrierservicecode=' + str(carrierservicecode) + '&carriercode='+ str(carriercode) + '&sessionID=' + session
            print("====", url)
            result = self.get_response(url, "GET", {})
            print("result", result)
            # {'PackageTypeDesc': 'LARGE FEDEX BOX', 'PackageTypeCode': 'LARGE BOX', 'CarrierCode': 0,#  'CarrierServiceCode': '01-DOM'}
            package_service_rec = self.env["package.services"]
            for r in result:
                package_service_id = package_service_rec.search(
                    [('name', '=', r.get('PackageTypeCode')), ('CarrierCode', '=', r.get('CarrierCode'))])
                if not package_service_id:
                    r['name'] = r.get('PackageTypeCode')
                    r['CarrierCode'] = str(r['CarrierCode'])
                    package_service_rec.create(r)
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

class ParcelProExceptions(models.Model):

    _name = "parcel.pro.exceptions"

    name = fields.Char('Name')
    api_type = fields.Selection([
        ('post_quotation', 'Post Quotation'),
        ('post_shipment', 'Fetch Carrier Services')], "API")
    message = fields.Text('Exception')
    date = fields.Date('Date', default=fields.Date.context_today, readonly=True)

