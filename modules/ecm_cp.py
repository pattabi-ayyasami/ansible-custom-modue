# !/usr/bin/python

import requests
import json
import time

from ansible.module_utils.basic import AnsibleModule
import ansible.module_utils.utils as utils
import ansible.module_utils.rest_client_util as rest_client_util

host = ""

def create_cp(data):  
    cp = {}
    cp["name"] = data.get("name")
    cp["type"] = data.get("type")
    cp["description"] = data.get("description")
    cp["address"] = data.get("address")
    cp["addressType"] = data.get("address_type")
    
    if data.get("vapp_id") is not None:
        vapp = {}
        vapp["id"] = data.get("vapp_id")
        cp["vapp"] = vapp
    
    if data.get("service_id") is not None:
        service = {}
        service["id"] = data.get("service_id")
        cp["service"] = service

    request_body = {}
    request_body["tenantName"] = "ECM"
    request_body["cp"] = cp
    
    url = "http://%(ecm_host_name)s/ecm_service/cps" % {"ecm_host_name": host}
    response = rest_client_util.perform_post(url, json.dumps(request_body))
    is_success, response = utils.process_response(response)

    if is_success:
        order_id  = response["data"]["order"]["id"]
        timeout_start = time.time()
        timeout = data.get("timeout", 3600)
        response, is_error = utils.wait_for_completion(order_id, timeout_start, timeout)
        if is_error:
            return False, False, response
        id = utils.get_cp_id(response)
        is_success, response = get_cp(id)
        return True, True, response

    return False, False, response


def get_cp(id):
    url = "http://%(ecm_host_name)s/ecm_service/cps/%(id)s" % \
          {"ecm_host_name": host, "id": id}
    response = rest_client_util.perform_get(url)
    return utils.process_response(response)

    

def main():
    fields = {
        "auth": {"required": False, "type": "dict"},
        "name": {"required": False, "type": "str"},
        "type": {"required": False, "type": "str"},
        "description": {"required": False, "type": "str"},
        "address": {"required": False, "type": "str"},
        "address_type": {"required": False, "type": "str"},
        "vapp_id": {"required": False, "type": "str"},
        "service_id": {"required": False, "type": "str"},
        "commection_parameters": {"required": False, "type": "dict" },
        "wait_for_completion": {"required": False, "default": True, "type": "bool" },
        "timeout": {"required": False, "default": 3600, "type": "int" },
        "state": {
            "default": "active", 
            "choices": ['active', 'deleted'],  
            "type": 'str' 
        },
    }

    choice_map = {
      "active": create_cp,
    }

    module = AnsibleModule(argument_spec=fields)
    is_success, has_changed, result = choice_map.get(module.params['state'])(module.params)
    if is_success:
        module.exit_json(changed=has_changed, id=result["data"]["cp"]["id"], cp=result["data"]["cp"])
    else:
        module.fail_json(msg='Error creating a connection point in ECM', result=result)


if __name__ == '__main__':
    main() 
