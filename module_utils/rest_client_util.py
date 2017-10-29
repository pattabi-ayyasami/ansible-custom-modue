import logging
import sys
import logging

import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.util import response

user_name = "xxx"
password = "xxx"
tenant_id = "xxx"

# http_basic_authentication = ("ecmadmin", "CloudAdmin123")
http_basic_authentication = (user_name, password)
headers = {}
headers["Content-Type"] = "application/json"
headers["TenantId"] = tenant_id

LOG = logging.getLogger(__name__)


def print_response(response):
    http_status_code = response.status_code
    LOG.debug("HTTP Status Code: %s", http_status_code)
    LOG.debug(response.content)


def is_success(http_status_code):
    if (http_status_code in (200, 201, 204)):
        return True
    return False


def get_value_from_response(response):
    http_status_code = response.status_code
    if (http_status_code in (200, 201)):
        return response.json().get("value")
    return None


def perform_get(url, request_body=None):
    LOG.debug("Perform GET: %s", url)
    response = requests.get(url, data=request_body, headers=headers, auth=http_basic_authentication)
    print_response(response)
    return response


def perform_post(url, request_body="{}", params=None):
    LOG.debug("Perform POST: %s", url)
    LOG.debug("Request Body: %s", request_body)
    LOG.debug("Request Params: %s", params)
    LOG.debug("Request Headers: %s", headers)

    response = requests.post(url, data=request_body, headers=headers,
                             auth=http_basic_authentication, params=params)
    print_response(response)
    return response


def perform_put(url, data=None, params=None, files=None):
    headers = {}
    headers["Content-Type"] = "multipart/form-data"

    LOG.debug("Perform PUT: %s", url)
    LOG.debug("Request Params: %s", params)
    LOG.debug("Request Headers: %s", headers)
    LOG.debug("Request Body: %s", data)
    LOG.debug("Request Files: %s", files)

    response = requests.put(url, headers=headers, params=params, files=files)
    print_response(response)
    return response


def perform_delete(url, request_body=None):
    LOG.debug("Perform DELETE: %s", url)
    response = requests.delete(url, data=request_body, headers=headers,
        auth=http_basic_authentication)
    print_response(response)
    return response
