import requests
from requests.auth import AuthBase

from configuration.models import Configuration


def get_eccr_search_api_url():
    """This method gets the ECCR search api url to query for records"""
    eccr_api = Configuration.objects.first()\
        .target_eccr_api
    if eccr_api[-1] != '/':
        eccr_api += '/'
    if not eccr_api.endswith('api/'):
        eccr_api += 'api/'
    eccr_api += 'sky/repo/search/'

    return eccr_api


def get_eccr_data_api_url():
    """This method gets the ECCR data api url to retrieve specific records"""
    eccr_api = Configuration.objects.first()\
        .target_eccr_api
    if eccr_api[-1] != '/':
        eccr_api += '/'
    if not eccr_api.endswith('api/'):
        eccr_api += 'api/'
    eccr_api += 'data/'

    return eccr_api


def search_eccr(query, type=None, start=0, length=20, auth=None):
    """
    search eccr for a query

    Args:
        query (string): the query to search ECCR for
        type (string): the object type to filter ECCR with
        start (int): how many results to skip
        length (int): how many results to return
        auth (requests.auth.AuthBase): the auth that should be used by the
            request object

    Returns:
        requests.Response: [dictionary]
    """
    data = {'searchParams': {"start": start, "size": length}}
    if type is not None:
        data['data'] = f'((@type:{type} OR (EncryptedValue AND ' +\
            f'encryptedType:{type})) AND {query}) AND NOT ' +\
            '(subType:"Progression")'
    else:
        data['data'] = f'({query}) AND NOT (subType:"Progression")'
    if auth is not None:
        return requests.post(get_eccr_search_api_url(),
                             auth=auth, timeout=3.0, data=data)
    else:
        return requests.post(get_eccr_search_api_url(), timeout=3.0, data=data)


def search_eccr_item(id, auth=None):
    """
    search eccr for a specific id

    Args:
        id (string): the id of the ECCR item to retrieve
        auth (requests.auth.AuthBase): the auth that should be used by the
            request object

    Returns:
        requests.Response: [dictionary]
    """
    data = {'data': f'(@id:"{id}")'}
    if auth is not None:
        return requests.post(get_eccr_search_api_url(),
                             auth=auth, timeout=3.0, data=data)
    else:
        return requests.post(get_eccr_search_api_url(), timeout=3.0, data=data)


def get_eccr_item(id, type, auth=None):
    """
    Get a specific item from the id and type

    Args:
        id (string): the id of the ECCR item to retrieve
        type (string): the object type of the ECCR item to retrieve
        auth (requests.auth.AuthBase): the auth that should be used by the
            request object

    Returns:
        requests.Response: [dictionary]
    """
    data = {'signatureSheet': []}
    if auth is not None:
        return requests.post(get_eccr_data_api_url() + f'{type}/{id}',
                             auth=auth, timeout=3.0, data=data)
    else:
        return requests.post(get_eccr_data_api_url() + f'{type}/{id}',
                             timeout=3.0, data=data)


class SignatureAuth(AuthBase):
    """Attaches HTTP Authorization Header to the given Request object."""

    def __init__(self, signature):
        super().__init__()
        self.sig = signature if isinstance(signature, list) else [signature,]

    def __call__(self, r):
        # modify and return the request

        r.data['signatureSheet'] = self.sig
        return r
