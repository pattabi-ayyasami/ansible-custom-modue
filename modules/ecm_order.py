# !/usr/bin/python

import requests
import json

from ansible.module_utils.basic import AnsibleModule
import ansible.module_utils.utils as utils
import ansible.module_utils.rest_client_util as rest_client_util


host = ""

def get_order(id):  
    url = "http://%(ecm_host_name)s/ecm_service/orders/%(id)s" % \
          {"ecm_host_name": host, "id": id}
    response = rest_client_util.perform_get(url)
    is_success, response = utils.process_response(response)

    meta = {'response': response}
    if is_success:
        return True, False, meta
    return False, False, meta
    

def main():
    fields = {
        "id": {"required": True, "type": "str" },
    }

    module = AnsibleModule(argument_spec=fields)
    
    is_success, has_changed, result = get_order(module.params.get("id"))
    if is_success:
        module.exit_json(changed=has_changed, order=result["data"]["order"])
    else:
        module.fail_json(msg='Error getting order details', meta=result)


if __name__ == '__main__':
    main() 
