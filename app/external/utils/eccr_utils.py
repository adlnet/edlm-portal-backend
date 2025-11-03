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


def get_eccr_item(id, item_type, auth=None):
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
        return requests.get(get_eccr_data_api_url() + f'{item_type}/{id}',
                            auth=auth, timeout=3.0, data=data)
    else:
        return requests.get(get_eccr_data_api_url() + f'{item_type}/{id}',
                            timeout=3.0, data=data)


def validate_eccr_item(reference):
    """
    Validate against reference from ECCR

    Args:
        reference (string): the reference type and
        id of the ECCR item to validate

    Returns:
        string: the name of the ECCR item if found, else None
    """
    try:
        item_type, item_id = reference.split('/', 1)
    except ValueError:
        raise ValueError("Invalid ECCR reference format, expected 'type/id'")

    resp = get_eccr_item(
        id=item_id,
        item_type=item_type
    )

    if resp.status_code == 200:
        try:
            name = resp.json().get('name', {}).get('@value', '')
            return name
        except ValueError:
            raise ValueError(
                "ECCR returned response is not JSON."
            )
    elif resp.status_code == 404:
        raise ValueError(
            "UUID does not exist in ECCR"
        )
    else:
        raise ConnectionError(
            "ECCR API error, check for more details."
        )


class SignatureAuth(AuthBase):
    """Attaches HTTP Authorization Header to the given Request object."""

    def __init__(self, signature):
        super().__init__()
        self.sig = signature if isinstance(signature, list) else [signature,]

    def __call__(self, r):
        # modify and return the request

        r.data['signatureSheet'] = self.sig
        return r
