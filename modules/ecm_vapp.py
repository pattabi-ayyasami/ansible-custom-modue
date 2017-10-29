# !/usr/bin/python
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import requests
import json
import time

from ansible.module_utils.basic import AnsibleModule
import ansible.module_utils.utils as utils
import ansible.module_utils.rest_client_util as rest_client_util

host = ""

def deploy_vapp(data):  
    vapp = {}
    vapp["name"] = data.get("name")
    vapp["type"] = data.get("type")
    vapp["flavor"] = data.get("flavor")
    vapp["description"] = data.get("description")

    product_info = {}
    product_info["vendor"] = data.get("vendor")
    product_info["version"] = data.get("version")
    vapp["productInfo"] = product_info

    config_data =[]
    parameters = data.get("parameters")
    if parameters:
        for name, value in parameters.items():
            parameter = {}
            parameter["name"] = name
            parameter["value"] = value
            config_data.append(parameter)
    vapp["configData"] = config_data

    config_files =[]
    vapp["configFiles"] = config_files

    hot_package = {}
    hot_package["vapp"] = vapp

    request_body = {}
    request_body["tenantName"] = "ECM"
    request_body["vdc"] = {}
    request_body["vdc"]["id"] = data.get("vdc")
    request_body["vimZoneName"] = data.get("vim_zone")
    request_body["hotPackage"] = hot_package

    hot_package_id = data.get("vnfd_id")
    url = "http://%(ecm_host_name)s/ecm_service/hotpackages/%(hot_package_id)s/deploy" % \
            {"ecm_host_name": host, "hot_package_id": hot_package_id}
    response = rest_client_util.perform_post(url, json.dumps(request_body))
    is_success, response = utils.process_response(response)
    if is_success:
        order_id  = response["data"]["order"]["id"]
        timeout_start = time.time()
        timeout = data.get("timeout", 3600)
        response, timed_out = utils.wait_for_completion(order_id, timeout_start, timeout)
        if timed_out:
            return False, False, response
        vapp_id = utils.get_vapp_id(response)
        is_success, response = get_vapp(vapp_id)
        return True, True, response

    return False, False, response
    
def delete_vapp(data=None):  
    id = data["id"]
    url = "http://%(ecm_host_name)s/ecm_service/vapps/%(vapp_id)s" % \
            {"ecm_host_name": host, "vapp_id": id}
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


def get_vapp(id):
    url = "http://%(ecm_host_name)s/ecm_service/vapps/%(vapp_id)s" % \
          {"ecm_host_name": host, "vapp_id": id}
    response = rest_client_util.perform_get(url)
    return utils.process_response(response)


def main():
    fields = {
        "auth": {"required": False, "type": "dict"},

        "id": {"required": False, "type": "str"},

        "name": {"required": False, "type": "str"},
        "vnfd_id": {"required": False, "type": "str"},
        "vdc": {"required": False, "type": "str"},
        "vim_zone": {"required": False, "type": "str"},
        "description": {"required": False, "type": "str"},
        "type": {"required": False, "type": "str"},
        "vendor": {"required": False, "type": "str"},
        "version": {"required": False, "type": "str"},
        "flavor": {"required": False, "type": "str"},
        "parameters": {"required": False, "type": "dict" },
        "wait_for_completion": {"required": False, "default": True, "type": "bool" },
        "timeout": {"required": False, "default": 3600, "type": "int" },
        "state": {
            "default": "active", 
            "choices": ['active', 'deleted'],  
            "type": 'str' 
        },
    }

    choice_map = {
      "active": deploy_vapp,
      "deleted": delete_vapp, 
    }

    module = AnsibleModule(argument_spec=fields)
    is_success, has_changed, result = choice_map.get(module.params['state'])(module.params)
    if is_success:
        if module.params["state"] == "active":
            vapp_id = result["data"]["vapp"]["id"]
            module.exit_json(changed=has_changed, id=vapp_id, vapp=result["data"]["vapp"])
        else:
            vapp_id = module.params["id"]
            module.exit_json(changed=has_changed, id=vapp_id)
    else:
        module.fail_json(msg='Error deploy/undeploy of vapp', meta=result)


if __name__ == '__main__':
    main() 
