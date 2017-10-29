# !/usr/bin/python

import requests
import json
import time

from ansible.module_utils.basic import AnsibleModule
import ansible.module_utils.utils as utils
import ansible.module_utils.rest_client_util as rest_client_util


host = ""

def create_service(data):  
    service = {}
    service["name"] = data.get("name")
    service["type"] = data.get("type")
    service["description"] = data.get("description")
    service["vendor"] = data.get("vendor")
    service["version"] = data.get("version")
    service["vdc"] = data.get("vdc")
    
    if data.get("vapps") is not None:
        vapps = []
        for item in data.get("vapps"):
            vapps.append(item)
        service["vapps"] = vapps

    if data.get("cps") is not None:
        cps = []
        for item in data.get("cps"):
            cps.append(item)
        service["cps"] = cps

    if data.get("additional_params") is not None:
        service["addionalParams"] = data.get("additional_params")

    if data.get("custom_input_params") is not None:
        service["customInputParams"] = data.get("custom_input_params")

    request_body = {}
    request_body["tenantName"] = "ECM"
    request_body["service"] = service
    
    url = "http://%(ecm_host_name)s/ecm_service/services" % {"ecm_host_name": host}
    response = rest_client_util.perform_post(url, json.dumps(request_body))
    is_success, response = utils.process_response(response)

    if is_success:
        order_id  = response["data"]["order"]["id"]
        timeout_start = time.time()
        timeout = data.get("timeout", 3600)
        response, is_error = utils.wait_for_completion(order_id, timeout_start, timeout)
        if is_error:
            return False, False, response
        service_id = utils.get_service_id(response)
        is_success, response = get_service(service_id)
        return True, True, response

    return False, False, response
    

def delete_service(data):  
    url = "http://%(ecm_host_name)s/ecm_service/services/%(id)s" % \
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
    

def get_service(id):
    url = "http://%(ecm_host_name)s/ecm_service/services/%(id)s" % \
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
        "vdc": {"required": False, "type": "str"},
        "vendor": {"required": False, "type": "str"},
        "version": {"required": False, "type": "str"},

        "vapps": {"required": False, "type": "list"},

        "cps": {"required": False, "type": "list"},

        "custom_input_params": {"required": False, "type": "dict"},
        "additional_params": {"required": False, "type": "dict"},

        "wait_for_completion": {"required": False, "default": True, "type": "bool" },
        "timeout": {"required": False, "default": 3600, "type": "int" },
        "state": {
            "default": "active", 
            "choices": ['active', 'deleted'],  
            "type": 'str' 
        },
    }

    choice_map = {
      "active": create_service,
      "deleted": delete_service,
    }

    module = AnsibleModule(argument_spec=fields)
    is_success, has_changed, result = choice_map.get(module.params['state'])(module.params)
    if is_success:
        if module.params["state"] == "active":
            id = result["data"]["service"]["id"]
            module.exit_json(changed=has_changed, id=id, service=result["data"]["service"])
        else:
            id = module.params["id"]
            module.exit_json(changed=has_changed, id=id)
    else:
        module.fail_json(msg='Error while create/delete of a service in ECM', result=result)


if __name__ == '__main__':
    main() 
