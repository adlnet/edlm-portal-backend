import logging
import requests
from dateutil.relativedelta import relativedelta
from requests.auth import AuthBase
from requests.exceptions import RequestException

from configuration.models import Configuration
from external.utils.eccr_utils import get_eccr_data_api_url

logger = logging.getLogger(__name__)


def get_elrr_api_url():
    """This method gets the elrr root api url"""
    elrr_api_url = Configuration.objects.first()\
        .target_elrr_api
    if elrr_api_url[-1] != '/':
        elrr_api_url += '/'
    if not elrr_api_url.endswith('api/'):
        elrr_api_url += 'api/'

    return elrr_api_url


class TokenAuth(AuthBase):
    """Attaches HTTP Authorization Header to the given Request object."""

    def __init__(self, token=None):
        if token is None:
            token = Configuration.objects.first().target_elrr_api_key
        super().__init__()
        self.token = token

    def __call__(self, r, token_name='Bearer'):
        # modify and return the request

        r.headers['Authorization'] = token_name + ' ' + self.token
        return r


def validate_person(person):
    """
    This method takes in a Person record and validates that
    necessary fields are populated

    False is returned if any required fields are missing
    """
    if ('firstName' not in person or not person['firstName']) and \
            ('name' not in person or not person['name']):
        return False
    if ('lastName' not in person or not person['lastName']) and \
            ('name' not in person or not person['name']):
        return False

    return True


def validate_elrr_goal(goal_data):
    """
    Validate ELRR Goal data has required fields
    """
    if not goal_data or not goal_data.get('id'):
        raise ValueError(
            'ELRR Goal data is empty or missing required field'
        )


def validate_elrr_competency(competency_data):
    """
    Validate ELRR Competency data has required fields
    """
    if not competency_data or not competency_data.get('id'):
        raise ValueError(
            'ELRR Competency data is empty or missing required field'
        )


def validate_elrr_learning_resource(learning_resource_data):
    """
    Validate ELRR Learning Resource data has required fields
    """
    if not learning_resource_data or not learning_resource_data.get('id'):
        raise ValueError(
            'ELRR Learning Resource data is empty or missing required field'
        )


def validate_elrr_person(person_data):
    """
    Validate ELRR Person data has required fields
    """
    if (not person_data or not person_data.get('id')
            or not validate_person(person_data)):
        raise ValueError(
            'ELRR Person data is empty or missing required field'
        )


def get_elrr_person_id_by_email(email):
    """
    Get ELRR Person UUID by email address

    Args:
        email: User's email address string

    Returns:
        ELRR Person UUID or None if not found
    """
    try:
        resp = requests.get(
            get_elrr_api_url() + 'person',
            params={'emailAddress': email},
            auth=TokenAuth(),
            timeout=3.0
        )

        if resp.status_code == 200:
            person = resp.json()

            if person:
                person = person[0]
                validate_elrr_person(person)
                return person['id']
            else:
                return None
        elif resp.status_code == 404:
            return None
        else:
            raise ConnectionError(
                'Error getting ELRR person by email'
            )
    except RequestException as e:
        logger.error(f'Error getting ELRR person by email: {e}')
        raise ConnectionError(
            'Error getting ELRR person by email,'
            ' check for more details'
        )


def create_elrr_person(learner):
    """
    Create a new Person in ELRR with email

    Args:
        learner: Portal learner instance

    Returns:
        ELRR Person UUID
    """
    try:
        person_data = {
            'firstName': learner.first_name,
            'lastName': learner.last_name,
            'name': f"{learner.first_name} {learner.last_name}",
            'emailAddresses': [
                {
                    'emailAddress': learner.email,
                }
            ]
        }

        resp = requests.post(
            get_elrr_api_url() + 'person',
            json=person_data,
            auth=TokenAuth(),
            timeout=3.0
        )

        if resp.status_code in [200, 201]:
            person = resp.json()
            validate_elrr_person(person)
            return person['id']
        else:
            raise ConnectionError(
                'Error creating ELRR person'
            )

    except RequestException as e:
        logger.error(f'Error creating ELRR person: {e}')
        raise ConnectionError(
            'Error creating ELRR person, check for more details'
        )


def get_or_create_elrr_person_by_email(learner):
    """
    Get or create ELRR Person by email address

    Args:
        learner: Portal learner instance

    Returns:
        ELRR Person UUID
    """
    person_id = get_elrr_person_id_by_email(learner.email)

    if person_id:
        return person_id

    # If no person found, create a new one
    person_id = create_elrr_person(learner)

    return person_id


def calculate_goal_achieved_by_date(start_date, timeline):
    """
    Calculate the goal achieved by date based on
    start date and goal timeline string

    Args:
        start_date: goal creation date (datetime)
        timeline: total month (int)

    Returns:
        start_date + months or none
    """
    if not timeline:
        return None

    return start_date + relativedelta(months=timeline)


def build_goal_data_for_elrr(learning_plan_goal, person_id):
    """
    Prepare LearningPlanGoal into ELRR Goal format

    Args:
        learning_plan_goal: LearningPlanGoal instance
        person_id: ELRR Person UUID string

    Returns:
        Dict formatted for ELRR Goal API
    """
    start_date = learning_plan_goal.created

    goal_data = {
        'personId': person_id,
        'goalId': f'portal-goal-{learning_plan_goal.id}',
        'name': learning_plan_goal.goal_name,
        'type': 'SELF',  # [SELF, ASSIGNED, or RECOMMENDED]
        'startDate': start_date.isoformat(),
    }

    achieved_by_date = calculate_goal_achieved_by_date(
        start_date,
        learning_plan_goal.timeline
    )

    if achieved_by_date:
        goal_data['achievedByDate'] = achieved_by_date.isoformat()

    return goal_data


def get_elrr_goal(elrr_goal_id):
    """
    Get ELRR goal by ID

    Args:
        elrr_goal_id: ELRR Goal UUID string

    Returns:
        goal data dict
    """
    try:
        resp = requests.get(
            f'{get_elrr_api_url()}goal/{elrr_goal_id}',
            auth=TokenAuth(),
            timeout=3.0
        )

        if resp.status_code == 200:
            goal_data = resp.json()
            validate_elrr_goal(goal_data)
            return goal_data
        elif resp.status_code == 404:
            raise ValueError(
                'ELRR Goal not found'
            )
        else:
            raise ConnectionError(
                'Elrr API error, failed to get ELRR goal'
            )

    except RequestException as e:
        logger.error(f'Error getting ELRR goal: {e}')
        raise ConnectionError('Error getting ELRR goal,'
                              ' check for more details')


def create_elrr_goal(goal_data):
    """
    Creates a new Goal in ELRR

    Args:
        goal_data: Dictionary prepared for ELRR Goal API
    """
    try:
        resp = requests.post(
            get_elrr_api_url() + 'goal',
            json=goal_data,
            auth=TokenAuth(),
            timeout=3.0
        )

        if resp.status_code in [200, 201]:
            goal_data = resp.json()
            validate_elrr_goal(goal_data)
            return goal_data
        else:
            raise ConnectionError(
                'ELRR API error, check for more details'
            )

    except RequestException as e:
        logger.error(f'Error creating ELRR goal: {e}')
        raise ConnectionError('Error creating ELRR goal,'
                              ' check for more details')


def update_elrr_goal(goal_data):
    """
    Update ELRR goal with goal data

    Args:
        goal_data: Dict prepared for ELRR Goal

    Returns:
        Updated goal data dict
    """
    try:
        goal_id = goal_data.get('id')
        if not goal_id:
            raise ValueError('Goal data missing id field for update operation')

        resp = requests.put(
            f'{get_elrr_api_url()}goal/{goal_id}',
            json=goal_data,
            auth=TokenAuth(),
            timeout=3.0
        )

        if resp.status_code == 200:
            goal_data = resp.json()
            validate_elrr_goal(goal_data)
            return goal_data
        else:
            raise ConnectionError(
                'Elrr API error, failed to get ELRR goal'
            )

    except RequestException as e:
        logger.error(f'Error updating ELRR goal: {e}')
        raise ConnectionError('Error updating ELRR goal,'
                              ' check for more details')


def remove_goal_from_elrr(elrr_goal_id):
    """
    Remove an ELRR goal by ID

    Args:
        elrr_goal_id: ELRR Goal UUID string

    Returns:
        True if deleted successfully
    """
    try:
        resp = requests.delete(
            f'{get_elrr_api_url()}goal/{elrr_goal_id}',
            auth=TokenAuth(),
            timeout=3.0
        )

        if resp.status_code == 204:
            return True
        elif resp.status_code == 404:
            raise ValueError(
                'ELRR Goal not found'
            )
        else:
            raise ConnectionError(
                'Elrr API error, failed to delete ELRR goal'
            )

    except RequestException as e:
        logger.error(f'Error deleting ELRR goal: {e}')
        raise ConnectionError('Error deleting ELRR goal,'
                              ' check for more details')


def sync_goal_updates_to_elrr(learning_plan_goal, updated_fields):
    """
    Sync updated fields of LearningPlanGoal to ELRR Goal

    Args:
        learning_plan_goal: LearningPlanGoal instance
        updated_fields: list of updated field names
    """
    # If no relevant field updated, return early
    if ('goal_name' not in updated_fields and
            'timeline' not in updated_fields):
        return

    elrr_goal_data = get_elrr_goal(
        str(learning_plan_goal.elrr_goal_id))

    if 'goal_name' in updated_fields:
        elrr_goal_data['name'] = learning_plan_goal.goal_name

    if 'timeline' in updated_fields:
        achieved_by_date = calculate_goal_achieved_by_date(
            learning_plan_goal.created,
            learning_plan_goal.timeline
        )

        elrr_goal_data['achievedByDate'] = achieved_by_date.isoformat()

    update_elrr_goal(elrr_goal_data)


def get_or_create_elrr_competency(reference, name):
    """
    Get or create an ELRR Competency by ECCR reference

    Args:
        reference: reference string
        name: name string

    Returns:
        ELRR Competency dict
    """
    try:
        eccr_data_url = get_eccr_data_api_url()

        get_resp = requests.get(
            get_elrr_api_url() + 'competency',
            params={'identifier': reference},
            auth=TokenAuth(),
            timeout=3.0
        )

        if get_resp.status_code == 200:
            competencies = get_resp.json()
            # If found existing competency, return now
            if competencies:
                competency = competencies[0]
                validate_elrr_competency(competency)
                return competency

        # If not get, create new competency
        competency_data = {
            'type': 'COMPETENCY',  # [COMPETENCY, CREDENTIA]
            'identifier': reference,
            'identifierUrl': f'{eccr_data_url}{reference}',
            'frameworkTitle': 'ECCR',
            'statement': name,
        }

        create_resp = requests.post(
            get_elrr_api_url() + 'competency',
            json=competency_data,
            auth=TokenAuth(),
            timeout=3.0
        )

        if create_resp.status_code in [200, 201]:
            competency = create_resp.json()
            validate_elrr_competency(competency)
            return competency
        else:
            raise ConnectionError(
                'Failed to create ELRR competency'
            )

    except RequestException as e:
        logger.error(f'Error with ELRR competency: {e}')
        raise ConnectionError('Error with ELRR competency,'
                              ' check for more details')


def store_ksa_to_elrr_goal(learning_plan_goal_ksa,
                           elrr_goal_id,
                           old_elrr_ksa_id=None):
    """
    Store a goal KSA to an ELRR goal and add it to the
    elrr goal's competencyIds array.
    If old_elrr_ksa_id is provided, remove it from the goal

    Args:
        learning_plan_goal_ksa: LearningPlanGoalKsa instance
        elrr_goal_id: ELRR Goal UUID string
        old_elrr_ksa_id (optional): ELRR Competency UUID string

    Returns:
        The ELRR competency UUID
    """
    ksa_reference = learning_plan_goal_ksa.eccr_ksa.reference
    ksa_name = learning_plan_goal_ksa.eccr_ksa.name

    elrr_competency = get_or_create_elrr_competency(
        ksa_reference, ksa_name)
    competency_id = elrr_competency.get('id')

    goal_data = get_elrr_goal(elrr_goal_id)
    competency_ids = goal_data.get('competencyIds', [])

    # If old ELRR competency ID provided, remove it
    if old_elrr_ksa_id and old_elrr_ksa_id in competency_ids:
        competency_ids.remove(old_elrr_ksa_id)

    # Add competency if not already existing in the arr
    if competency_id not in competency_ids:
        competency_ids.append(competency_id)

    goal_data['competencyIds'] = competency_ids
    update_elrr_goal(goal_data)

    return competency_id


def remove_ksa_from_elrr_goal(elrr_goal_id, elrr_competency_id):
    """
    Remove a competency from an ELRR goal's competencyIds array

    Args:
        elrr_goal_id: ELRR Goal UUID string
        elrr_competency_id: ELRR Competency UUID string
    """
    goal_data = get_elrr_goal(elrr_goal_id)

    # Remove competency from arr
    competency_ids = goal_data.get('competencyIds', [])
    if elrr_competency_id in competency_ids:
        competency_ids.remove(elrr_competency_id)
        goal_data['competencyIds'] = competency_ids
        update_elrr_goal(goal_data)


def get_or_create_elrr_learning_resource(reference, name):
    """
    Get or create an ELRR Learning Resource by XDS reference

    Args:
        reference: reference string
        name: name string

    Returns:
        ELRR LearningResource dict

    """
    try:
        get_resp = requests.get(
            get_elrr_api_url() + 'learningresource',
            params={'iri': reference},
            auth=TokenAuth(),
            timeout=3.0
        )

        if get_resp.status_code == 200:
            learning_resources = get_resp.json()
            if learning_resources:
                learning_resource = learning_resources[0]
                validate_elrr_learning_resource(learning_resource)
                return learning_resource

        # Create new learning resource
        learning_resource_data = {
            'iri': reference,
            'title': name,
        }

        create_resp = requests.post(
            get_elrr_api_url() + 'learningresource',
            json=learning_resource_data,
            auth=TokenAuth(),
            timeout=3.0
        )

        if create_resp.status_code in [200, 201]:
            learning_resource = create_resp.json()
            validate_elrr_learning_resource(learning_resource)
            return learning_resource
        else:
            raise ConnectionError(
                'ELRR API error, check for more details.'
            )

    except RequestException as e:
        logger.error(f'Error with ELRR learning resource: {e}')
        raise ConnectionError('Error with ELRR learning resource,'
                              ' check for more details')


def store_course_to_elrr_goal(learning_plan_goal_course,
                              elrr_goal_id,
                              old_elrr_course_id=None):
    """
    Store a course to an ELRR goal and add it to
    the goal's learningResourceIds array.
    If old_elrr_course_id is provided, remove it from the goal

    Args:
        learning_plan_goal_course: PlanGoalCourse instance
        elrr_goal_id: ELRR Goal UUID string
        old_elrr_course_id (optional): ELRR LR UUID string to remove
    Returns:
        The ELRR learning resource UUID
    """
    course_reference = learning_plan_goal_course.xds_course.reference
    course_name = learning_plan_goal_course.xds_course.name

    elrr_learning_resource = get_or_create_elrr_learning_resource(
        course_reference, course_name)
    learning_resource_id = elrr_learning_resource.get('id')

    goal_data = get_elrr_goal(elrr_goal_id)
    learning_resource_ids = goal_data.get('learningResourceIds', [])

    # If old ELRR course ID provided, remove it
    if old_elrr_course_id and old_elrr_course_id in learning_resource_ids:
        learning_resource_ids.remove(old_elrr_course_id)

    # Add learning resource if not already existing in the arr
    if learning_resource_id not in learning_resource_ids:
        learning_resource_ids.append(learning_resource_id)

    goal_data['learningResourceIds'] = learning_resource_ids
    update_elrr_goal(goal_data)

    return learning_resource_id


def remove_course_from_elrr_goal(elrr_goal_id, elrr_learning_resource_id):
    """
    Remove a learning resource from an ELRR goal's
    learningResourceIds array

    Args:
        elrr_goal_id: ELRR Goal UUID string
        elrr_learning_resource_id: ELRR Learning Resource UUID string
    """
    goal_data = get_elrr_goal(elrr_goal_id)

    # Remove learning resource from array
    learning_resource_ids = goal_data.get('learningResourceIds', [])
    if elrr_learning_resource_id in learning_resource_ids:
        learning_resource_ids.remove(elrr_learning_resource_id)
        goal_data['learningResourceIds'] = learning_resource_ids
        update_elrr_goal(goal_data)
