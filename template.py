import requests
import json
import os
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

class HttpMethod:

    """
    HttpMethod will have methods to send
    GET, POST, PATCH, PUT, DELETE request to the initalized url
    """
   
    def __init__(self, extension, session, **kwargs):
        self.url = "https://api.intra.42.fr{}".format(extension)
        self.filter = kwargs["filter"] if "filter" in kwargs else {}
        self.page = kwargs["pages"] if "pages" in kwargs else {'size':100, 'number':1}
        self.sort = kwargs["sort"] if "sort" in kwargs else ""
        self.session = session

    def ParseParams(self):

        filter_query = "&".join([f"filter[{key}]={value}" for key, value in self.filter.items()]) if self.filter else ""
        page_query = "&".join([f"page[{key}]={value}" for key, value in self.page.items()]) if self.page else ""

        result = filter_query or page_query
        if filter_query and page_query:
            result = f"?{filter_query}&{page_query}"

        if self.sort:
            if result:
                result += f"&sort={self.sort}"
            else:
                result = f"sort={self.sort}"

        return f"?{result}" if result else ""
 
    def Get(self):
        """
        return json
        """
        response = self.session.get(self.url + self.ParseParams())
        response.raise_for_status()
        if self.page and "number" in self.page: self.page['number'] += 1
        return json.loads(response.text)

    def Post(self, data):
        """
        return response Object
        """
        response = self.session.post(self.url, json=data)
        response.raise_for_status()
        return response

    def Patch(self, data):
        """
        return response Object
        """
        response = self.session.patch(self.url, json=data)
        response.raise_for_status()
        return response

    def Put(self, data):
        """
        return response Object
        """
        response = self.session.put(self.url, json=data)
        response.raise_for_status()
        return response

    def Delete(self):
        """
        return response Object
        """
        response = self.session.delete(self.url)
        response.raise_for_status()
        return response

class FtApi:

    def __init__(self, uid, secret, code=None, redirect=None, bearer=None):
        self.uid = uid
        self.secret = secret
        self.code = code
        self.redirect = redirect
        self.bearer = bearer
        if self.bearer is None:
            try:
                self.bearer = self.GetBearer()
            except Exception as e:
                raise Exception(e)
        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'Bearer {}'.format(self.bearer)})

    def GetBearer(self):
        """
        Makes a call to get Bearer with your crendentials
        return: string
        """
        if self.code:
            payload = {'grant_type':'authorization_code', 'client_id': self.uid,
                    'client_secret': self.secret, 'code':self.code, 'redirect_uri':self.redirect}
        else:
            payload = {'grant_type':'client_credentials', 'client_id': self.uid,
                    'client_secret': self.secret}
        try:
            response = requests.post("https://api.intra.42.fr/oauth/token", data=payload)
            if response.status_code != 200:
                raise Exception("wrong status_code:{}".format(response.status_code))
            parsed_response = json.loads(response.content.decode('utf-8'))
        except Exception as e:
            raise Exception(e)
        
        return parsed_response['access_token']

    def ReloadBearer(self):
        """
        Use this method in case 'The access token expired'
        """
        self.bearer = self.GetBearer()
        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'Bearer {}'.format(self.bearer)})

    def RawEndpoint(self, endpoint):
        """
        parameter : string
        return : HttpMethod
        
        Create a HttpMethod with passed parameter as the endpoint for "https://api.intra.42.fr/"

        example :"/v2/users?filter[pool_year]=2019&page[size]=100&page[number]=3"
        """
        return HttpMethod(endpoint, self.session)

    def ColorizeJsonOutput(self, jsonObject):
        jsonStr = json.dumps(jsonObject, indent=4, sort_keys=True)
        print(highlight(jsonStr, JsonLexer(), TerminalFormatter()))
