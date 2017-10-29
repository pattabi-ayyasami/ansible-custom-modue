# !/usr/bin/python

import requests
import json
import time

from ansible.module_utils.basic import AnsibleModule
import ansible.module_utils.rest_client_util as rest_client_util
import ansible.module_utils.utils as utils


host = ""

def create_vlink(data):  
    vlink = {}
    vlink["name"] = data.get("name")
    vlink["type"] = data.get("type")
    vlink["description"] = data.get("description")
    vlink["vendor"] = data.get("vendor")
    vlink["version"] = data.get("version")
    vlink["providerVlId"] = data.get("provider_vl_id")
    
    if data.get("service_id") is not None:
        service = {}
        service["id"] = data.get("service_id")
        vlink["service"] = service

    if data.get("cps") is not None:
        cps = []
        for item in data.get("cps"):
            cps.append(item)
        vlink["cps"] = cps

    #vlink["addionalParams"] = data.get("additional_params")
    #vlink["customInputParams"] = data.get("custom_input_params")

    request_body = {}
    request_body["tenantName"] = "ECM"
    request_body["vlink"] = vlink
    
    url = "http://%(ecm_host_name)s/ecm_service/vlinks" % {"ecm_host_name": host}
    response = rest_client_util.perform_post(url, json.dumps(request_body))
    is_success, response = utils.process_response(response)
    if is_success:
        order_id  = response["data"]["order"]["id"]
        timeout_start = time.time()
        timeout = data.get("timeout", 3600)
        response, is_error = utils.wait_for_completion(order_id, timeout_start, timeout)
        if is_error:
            return False, False, response
        vlink_id = utils.get_vlink_id(response)
        is_success, response = get_vlink(vlink_id)
        return True, True, response

    return False, False, response
    

def delete_vlink(data):  
    url = "http://%(ecm_host_name)s/ecm_service/vlinks/%(id)s" % \
            {"ecm_host_name": host, "id": data.get("id")}
    response = rest_client_util.perform_delete(url)
    is_success, response = utils.process_response(response)
    if is_success:
        order_id  = response["data"]["order"]["id"]
        timeout_start = time.time()
        timeout = data.get("timeout", 3600)
        response, timed_out = utils.wait_for_completion(order_id, timeout_start, timeout)
        if timed_out:
            return False, False, response
        return True, True, response

    return False, False, response
    

def get_vlink(id):
    url = "http://%(ecm_host_name)s/ecm_service/vlinks/%(id)s" % \
          {"ecm_host_name": host, "id": id}
    response = rest_client_util.perform_get(url)
    return utils.process_response(response)


def main():
    fields = {
        "auth": {"required": False, "type": "dict"},
        "id": {"required": False, "type": "str"},
        "name": {"required": False, "type": "str"},
        "type": {"required": False, "type": "str"},
        "description": {"required": False, "type": "str"},
        "vendor": {"required": False, "type": "str"},
        "version": {"required": False, "type": "str"},
        "service_id": {"required": False, "type": "str"},
        "provider_vl_id": {"required": False, "type": "str" },
        "cps": {"required": False, "type": "list" },
        "additional_params": {"required": False, "type": "dict" },
        "custom_input_params": {"required": False, "type": "dict" },
        "wait_for_completion": {"required": False, "default": True, "type": "bool" },
        "timeout": {"required": False, "default": 3600, "type": "int" },
        "state": {
            "default": "active", 
            "choices": ['active', 'deleted'],  
            "type": 'str' 
        },
    }

    choice_map = {
      "active": create_vlink,
      "deleted": delete_vlink,
    }

    module = AnsibleModule(argument_spec=fields)
    is_success, has_changed, result = choice_map.get(module.params['state'])(module.params)
    if is_success:
        if module.params["state"] == "active":
            id = result["data"]["vlink"]["id"]
            module.exit_json(changed=has_changed, id=id, vlink=result["data"]["vlink"])
        else:
            id = module.params["id"]
            module.exit_json(changed=has_changed, id=id)
    else:
        module.fail_json(msg='Error while create/delete of a virtual link in ECM', result=result)


if __name__ == '__main__':
    main() 
