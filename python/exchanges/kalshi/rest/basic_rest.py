import inspect
import json
import os
import requests
from ..authenticator import Authenticator

from typing import Dict, Any, Optional

class BasicRest:
    def __init__(self):
        self.auth = Authenticator()
        self.base_url = self.auth.PROD_URL + self.auth.PROD_PATH

    def save_json(self, json_object, name):
        os.makedirs("json/kalshi", exist_ok=True)

        with open("json/kalshi/" + name + ".json", "w") as f:
            json.dump(json_object, f, indent=4)

        return json_object

    def get_kwargs(self):
        #Inspects a frame higher in the call stack to get all arguments passed to the function
        frame = inspect.currentframe().f_back
        #Gets list of argument names and their associated values
        keys, _, _, values = inspect.getargvalues(frame)
        kwargs = {}
        for key in keys:
            if key == "self":
                continue
            kwargs[key] = values[key]
        return kwargs

    def drop_none(self, kwargs: dict):
        return {i: kwargs[i] for i in kwargs if kwargs[i] is not None}
    
    def get(self, url, headers=None, timeout=30, **kwargs) -> Dict[str, Any]:
        #Checks if any boolean values are in kwargs and converts them to lowercase strings
        for i in kwargs:
            if isinstance(kwargs[i], bool):
                kwargs[i] = str(kwargs[i]).lower()

        #Uses all provided kwargs as query parameters (not just boolean ones)
        response = requests.get(url, params=kwargs, headers=headers, timeout=timeout)
        if response.status_code != 200:
            raise Exception(response.content.decode())
        return json.loads(response.content)
    
    def post(self, url, headers=None, body=None, timeout=30) -> Dict[str, Any]:
        response = requests.post(url, headers=headers, json=body, timeout=timeout)

        valid_response_codes = [200, 201]
        if response.status_code not in valid_response_codes:
            raise Exception(response.content.decode())
        return json.loads(response.content)
    
    def put(self, url, headers=None, body=None, timeout=30) -> Dict[str, Any]:
        response = requests.put(url, headers=headers, json=body, timeout=timeout)
        if response.status_code != 200:
            raise Exception(response.content.decode())
        return json.loads(response.content)
    
    def delete(self, url, headers=None, body=None, timeout=30) -> Dict[str, Any]:
        response = requests.delete(url, headers=headers, json=body, timeout=timeout)
        if response.status_code != 200:
            raise Exception(response.content.decode())
        return json.loads(response.content)
    
    def _authenticated_get_request(self, url: str, **kwargs):
        return self.get(url, headers=self.auth.create_headers(url, "GET"), **kwargs)

    def _authenticated_post_request(self, url: str, data: dict = None):
        return self.post(url, headers=self.auth.create_headers(url, "POST"), body=data)
    
    def _authenticated_put_request(self, url: str, data: dict = None):
        return self.put(url, headers=self.auth.create_headers(url, "PUT"), body=data)

    def _authenticated_del_request(self, url: str, data: dict = None):
        return self.delete(url, headers=self.auth.create_headers(url, "DELETE"), body=data)

    