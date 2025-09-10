# Enterprise Digital Learning Management: Portal-Backend
The Enterprise Digital Learning Management (EDLM) Portal Backend is the consolidated backend to the human-facing Portal UI application, enabling complex data processing across multiple data sources. Because the Portal Backend is a separate application, it can be deployed in a separate environment from the connected services. It can even be configured to point to different deployments (ECC, ELRR, ECCR, Moodle, etc.) as needed. In addition, multiple Portal Backend applications can be deployed and point to the same instances, allowing for excellent installation and configuration flexibility. 


## Environment variables
- The following environment variables are required:

| Environment Variable      | Description |
| ------------------------- | ----------- |
| CSRF_COOKIE_DOMAIN            | The domain to be used when setting the CSRF cookie. This can be useful for easily allowing cross-subdomain requests to be excluded from the normal cross site request forgery protection. |
| CSRF_TRUSTED_ORIGINS            | A list of trusted origins for unsafe requests |
| DB_HOST                   | The host name, IP, or docker container name of the database |
| DB_NAME                   | The name to give the database |
| DB_PASSWORD               | The password for the user to access the database |
| DB_PORT                   | The port to use to access the database |
| DB_USER                   | The name of the user to use when connecting to the database. When testing use root to allow the creation of a test database |
| DJANGO_SUPERUSER_EMAIL    | (OPTIONAL) The email of the superuser that will be created in the application |
| DJANGO_SUPERUSER_PASSWORD | (OPTIONAL) The password of the superuser that will be created in the application |
| DJANGO_SUPERUSER_USERNAME | (OPTIONAL) The username of the superuser that will be created in the application |
| FORCE_SCRIPT_NAME         | (OPTIONAL) The path prefix to use for routing of requests |
| HOSTS                     | A list of host names, separated by semicolons, that the application should accept requests for |
| LOG_PATH                  | The path to the log file to use |
| SECRET_KEY_VAL            | The Secret Key for Django |
| XAPI_USE_JWT                        | If this variable is set, attempt to use the value of a JWT auth token to derive the xAPI actor account. If not set the actor will be identified by mbox email
| XAPI_ACTOR_ACCOUNT_HOMEPAGE |  Set the `$.actor.account.homePage` field on xAPI Statements. Only used when `XAPI_USE_JWT` is `true`
| XAPI_ACTOR_ACCOUNT_NAME_JWT_FIELDS  | A comma-separated list of fields to check in the JWT for the `$.actor.account.name` field on xAPI Statements. The first non-empty string found will be chosen. Defaults to `activecac,preferred_username`. Only used when `XAPI_USE_JWT` is `true`

## Configuration for EDLM Portal Backend

<details><summary> Troubleshooting the EDLM Portal Backend</summary>

A good basic troubleshooting step is to use `docker-compose down` and then `docker-compose up --build` to rebuild the app image; however, this will delete everything in the database.

| Troubleshooting  | Description |
| ------------- | ------------- |
| Line Endings      |  If the container builds but crashes or logs an error of unrecognized commands, the issue is usually incorrect line endings.</br> </br> Most IDEs/Text Editors allow changing the line endings, but the dos2unix utility can also be used to change the line endings of `start-app.sh` and `start-server.sh` to LF.|
</details>

<details><summary> Updating the EDLM Portal Backend</summary>

To update an existing installation: 

1. Pull the latest changes using git

2. Restart the application using `docker-compose restart`

</details>

<details><summary> EDLM Portal Backend Authentication </summary>

Information on the settings for the authentication module can be found on the [P1-Auth repo](https://github.com/OpenLXP/p1-auth) and [django-rest-knox documentation](https://jazzband.github.io/django-rest-knox/).

</details>

<details><summary> ECC XDS Authorization</summary>

The environment variables `SU_FLAG`, `SU_VALUE` , `STAFF_FLAG`, and `STAFF_VALUE` should be defined (if using docker-compose the variables can be passed through) to automate Staff and Super User access.

Additional permission automation can be done using `RelatedAssignment` and `AttributeCheck` within the Django Admin.

</details>

# Deployment
The EDLM Portal Backend is deployed using Docker containers. Docker containers are portable, scalable, and reliable. EDLM Docker images will be stored in the public IronBank's Repo1 registry to allow anyone to pull and deploy the image. Docker images are also cloud agnostic which allows for deployment on any cloud provider. Images can be deployed as a single Docker image, a cloud provided container service, and Kubernetes for orchestration. The EDLM deploys component images on Kubernetes to orchestrate containers for scalability, reliability, and high availability.

## Testing

### Component Testing & CI/CD

The EDLM Portal Backend uses Pylint and Coverage for code coverage testing. To run the automated tests on the application run the command below

### End to End Testing

The EDLM Portal Backend uses cypress for system end to end testing.

# Authentication

We are using our P1-Auth package to handle authentication of P1 users.

Information on the settings for the authentication module can be found on the [P1-Auth repo](https://github.com/OpenLXP/p1-auth).

# Authorization

Using Django's Admin system, permissions can be applied to a specific user or group.  The P1-Auth package allows automating associations, which can be used to assign permissions as needed.
