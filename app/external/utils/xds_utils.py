import json
from datetime import timedelta

import requests
from django.utils import timezone
from requests.auth import AuthBase
from rest_framework import status
from rest_framework.response import Response

from configuration.models import Configuration
from external.models import Course


def get_course_name(response):
    """
    This method retrieves the course name from a P2881 formatted response
    object or None if unable to find the course name

    Args:
        response (requests.Response): the response object

    Returns:
        String: [course name]
    """
    metadata_dict = response.json()
    if ('p2881-core' in metadata_dict and
            'Title' in metadata_dict['p2881-core']):
        return metadata_dict['p2881-core']['Title']
    return None


def format_metadata(exp_record):
    """This method takes in a record and converts it to an XSE format"""
    result = None

    if 'metadata' in exp_record:
        metadataObj = exp_record['metadata']

        if 'Metadata_Ledger' in metadataObj:
            result = metadataObj['Metadata_Ledger']
            result["Supplemental_Ledger"] = \
                (metadataObj["Supplemental_Ledger"] if "Supplemental_Ledger" in
                 metadataObj else None)
            meta = {}

            meta["id"] = exp_record["unique_record_identifier"]
            meta["metadata_key_hash"] = exp_record["metadata_key_hash"]
            result["meta"] = meta

    return result


def metadata_to_target(metadata_JSON):
    """This method takes in a JSON representation of a record and transforms it
        into the search engine format"""
    metadata_dict = json.loads(metadata_JSON)
    result = None

    if isinstance(metadata_dict, list):
        result_list = []

        for record in metadata_dict:
            formatted_record = format_metadata(record)
            result_list.append(formatted_record)

        result = result_list

    elif isinstance(metadata_dict, dict):
        formatted_record = format_metadata(metadata_dict)
        result = formatted_record

    return result


def get_courses_api_url(course_id):
    """This method gets the metadata api url to fetch single records"""
    composite_api_url = Configuration.objects.first()\
        .target_xds_api
    if composite_api_url[-1] != '/':
        composite_api_url += '/'
    if not composite_api_url.endswith('api/'):
        composite_api_url += 'api/'
    composite_api_url += 'experiences/'
    full_api_url = composite_api_url + course_id

    return full_api_url


def save_courses(course_list):
    """
    This method handles the saving of each course in the list

    Args:
        course_list (list): a list of tuples (metadata_key_hash, course_name)
    """
    time_difference = timedelta(days=1)
    course_name_length = 255
    for course_hash, course_name in course_list:
        experience, new = \
            Course.objects.get_or_create(reference=course_hash)
        if new or experience.modified < timezone.now() - time_difference:
            experience.name = course_name[:course_name_length]
            experience.save()


def handle_unauthenticated_user():
    """This method returns an HTTP response if user is not authenticated"""
    return Response({'Access Denied: Unauthenticated user.'},
                    status.HTTP_401_UNAUTHORIZED)


# helper function to get an experience from XDS
def get_xds_experience(experience_id, auth=None):
    """
    Get a specific experience from a specific catalog

    Args:
        experience_id (string): the metadata_key_hash for the experience
        auth (requests.auth.AuthBase): the auth that should be used by the
            request object

    Returns:
        requests.Response: [dictionary]
    """
    if auth is not None:
        return requests.get(get_courses_api_url(experience_id),
                            auth=auth, timeout=3.0)
    else:
        return requests.get(get_courses_api_url(experience_id),
                            timeout=3.0)


def validate_xds_course(reference):
    """
    Validate against reference from XDS

    Args:
        reference (string): the reference of the XDS experience to validate

    Returns:
        string: the name of the XDS experience if found, else None
    """

    resp = get_xds_experience(
        experience_id=reference,
    )

    if resp.status_code == 200:
        try:
            name = get_course_name(resp)
            return name
        except ValueError:
            raise ValueError(
                "XDS returned response is not JSON. "
            )
    elif resp.status_code == 404:
        raise ValueError(
            "Reference does not exist in XDS"
        )
    else:
        raise ConnectionError(
            "XDS API error, check for more details."
        )


class TokenAuth(AuthBase):
    """Attaches HTTP Authorization Header to the given Request object."""

    def __init__(self, token):
        super().__init__()
        self.token = token

    def __call__(self, r, token_name='Bearer'):
        # modify and return the request

        r.headers['Authorization'] = token_name + ' ' + self.token
        return r
