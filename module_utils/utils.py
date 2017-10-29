# !/usr/bin/python

import requests
import json
import time
import ansible.module_utils.rest_client_util as rest_client_util


interval = 5
host = "10.61.156.70:8080"


CREATE_SERVICE = "createService"
DEPLOY_HOT_PACKAGE = "deployHotPackage"
CREATE_VLINK = "createVLink"
CREATE_CP = "createCp"

def get_vapp_id(response):
     order_items = response["data"]["order"]["orderItems"]
     for item in order_items:
         item_name = next(iter(item))
         if item_name == "deployHotPackage":
             return item["deployHotPackage"]["id"]
         

def get_service_id(response):
     order_items = response["data"]["order"]["orderItems"]
     for item in order_items:
         item_name = next(iter(item))
         if item_name == "createService":
             return item["createService"]["id"]
         

def get_vlink_id(response):
     order_items = response["data"]["order"]["orderItems"]
     for item in order_items:
         item_name = next(iter(item))
         if item_name == "createVLink":
             return item["createVLink"]["id"]

         
def get_cp_id(response):
     order_items = response["data"]["order"]["orderItems"]
     for item in order_items:
         item_name = next(iter(item))
         if item_name == "createCp":
             return item["createCp"]["id"]

def extract_id_from_order_response(response, operation_name):
     order_items = response["data"]["order"]["orderItems"]
     for item in order_items:
         item_name = next(iter(item))
         if item_name == operation_name:
             return item[operation_name]["id"]

         
def wait_for_completion(order_id, timeout_start, timeout):
     order_status = None
     response = None
     error_response = { "response": "operation did not complete within the specified timeout value" }
     is_error = True
     while time.time() < timeout_start + timeout:
         url = "http://%(ecm_host_name)s/ecm_service/orders/%(id)s" % \
               {"ecm_host_name": host, "id": order_id}
         response = rest_client_util.perform_get(url)
         is_success, response = process_response(response)
         order_status = response["data"]["order"]["orderReqStatus"]
         if order_status not in [ "COM", "ERR" ] :
             time.sleep(interval)
         else:
             if order_status == "COM":
                 is_error = False
             else:
                 error_response = response
             break
     
     if is_error:
         return error_response, is_error
     return response, is_error

def process_response(response):
    try:
        response_dict = response.json()
        status = response_dict.get("status")
        request_status = status.get("reqStatus")
        if request_status != "SUCCESS":
            return False, response_dict
        return True, response_dict
    except:
        print response.content
        print "Response is not in JSON format"
        return False, {}

