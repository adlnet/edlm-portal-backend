import json
from unittest.mock import patch

from django.test import tag
from django.urls import reverse
from rest_framework import status

from .test_setup import TestSetUp


@tag('unit')
class ViewTests(TestSetUp):

    def test_profile_question_requests_no_auth(self):
        """Test that making a get request to the profile question api with no
        auth returns an error"""
        url = reverse('api:profile-questions-detail', kwargs={"pk": 1})
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = "Authentication credentials were not provided."

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(responseDict['detail'], expected_error)

    def test_profile_question_requests_bad_id(self):
        """Test that making a get request to the profile question api with a
        bad id returns an error"""
        url = reverse('api:profile-questions-detail', kwargs={"pk": 1})
        self.client.login(username=self.auth_email,
                          password=self.auth_password)
        response = self.client.get(url)
        responseDict = json.loads(response.content)
        expected_error = "No ProfileQuestion matches the given query."

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(responseDict['detail'], expected_error)

    # def test_schemaledger_requests_no_version(self):
    #     """Test that making a get request to the schema api with just a schema
    #         name should return the latest version"""
    #     url = "%s?name=test_name" % (reverse('api:schemaledger'))
    #     self.sourceSchema.save()
    #     with patch('api.views.TermSet.objects') as schemaObj:
    #         schemaObj.return_value = schemaObj
    #         schemaObj.all.return_value = schemaObj
    #         schemaObj.filter.return_value = schemaObj
    #         schemaObj.order_by.return_value = schemaObj
    #         schemaObj.first.return_value = self.sourceTS

    #         response = self.client.get(url)
    #         responseDict = json.loads(response.content)
    #         self.assertEqual(response.status_code, status.HTTP_200_OK)
    #         self.assertEqual(responseDict["iri"], self.sourceTS.iri)

    # def test_schemaledger_requests_no_version_found(self):
    #     """Test that making a get request to the schema api with a version
    #         that doesn't exist returns an error"""
    #     url = f"%s?name={self.sourceSchema.schema_name}&version=9.9.9" % (
    #         reverse('api:schemaledger'))

    #     self.sourceSchema.save()

    #     response = self.client.get(url)
    #     responseDict = json.loads(response.content)
    #     expected_error = ["Error; no schema found for version '9.9.9'"]

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(responseDict['message'], expected_error)

    # def test_schemaledger_requests_iri(self):
    #     """Test that making a get request to the schema api with just an
    #         iri should return the latest version"""
    #     self.sourceSchema.save()
    #     url = f"%s?iri={self.sourceSchema.schema_iri}" % (
    #         reverse('api:schemaledger'))
    #     with patch('api.views.TermSet.objects') as schemaObj:
    #         schemaObj.return_value = schemaObj
    #         schemaObj.all.return_value = schemaObj
    #         schemaObj.filter.return_value = schemaObj
    #         schemaObj.order_by.return_value = schemaObj
    #         schemaObj.first.return_value = self.sourceTS

    #         response = self.client.get(url)
    #         responseDict = json.loads(response.content)
    #         self.assertEqual(response.status_code, status.HTTP_200_OK)
    #         self.assertEqual(responseDict["iri"], self.sourceTS.iri)

    # def test_schemaledger_requests_iri_fail(self):
    #     """Test that making a get request to the schema api with just an
    #         iri should fail correctly"""
    #     url = "%s?iri=bad" % (reverse('api:schemaledger'))

    #     response = self.client.get(url)

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_schemaledger_requests_all_params(self):
    #     """Test that making a get request to the schema api with just all
    #         query params returns a valid object"""
    #     url = "%s?name=test_name&version=1.2.3" % (reverse('api:schemaledger'))
    #     self.sourceSchema.save()
    #     with patch('api.views.TermSet.objects') as schemaObj:
    #         schemaObj.return_value = schemaObj
    #         schemaObj.all.return_value = schemaObj
    #         schemaObj.filter.return_value = schemaObj
    #         schemaObj.order_by.return_value = schemaObj
    #         schemaObj.first.return_value = self.sourceTS

    #         response = self.client.get(url)
    #         responseDict = json.loads(response.content)

    #         self.assertEqual(response.status_code, status.HTTP_200_OK)
    #         self.assertEqual(responseDict["iri"], self.sourceTS.iri)

    # def test_schemaledger_requests_no_schema_found(self):
    #     """Test that making a get request to the schema api with just a schema
    #         that doesn't exist returns an error"""
    #     url = "%s?name=test&version=1.0.2" % (reverse('api:schemaledger'))

    #     response = self.client.get(url)
    #     responseDict = json.loads(response.content)
    #     expected_error = ["Error; no schema found with the name 'test'"]

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(responseDict['message'], expected_error)

    # def test_transformationledger_requests_no_param(self):
    #     """Test that making a get request to the mappings api with no query
    #         params returns errors for each required parameter"""
    #     url = reverse('api:transformationledger')
    #     response = self.client.get(url)
    #     responseDict = json.loads(response.content)
    #     expected_error = ["Error; query parameter 'sourceName' or "
    #                       "'sourceIRI' is required", "Error; query parameter"
    #                       " 'targetName' or 'targetIRI' is required"]
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(responseDict['message'], expected_error)

    # def test_transformationledger_requests_no_mapping_found(self):
    #     """Test that making a get request to the mappings api with all params
    #         fails when no transformationledger is found"""
    #     url = ("%s?sourceName=test&sourceVersion=1.0.2&targetName=test2&" +
    #            "targetVersion=1.0.0") % (reverse('api:transformationledger'))

    #     with patch('api.views.TermSet.objects') as mappingObj:
    #         mappingObj.return_value = mappingObj
    #         mappingObj.all.return_value = mappingObj
    #         mappingObj.filter.return_value = None

    #         response = self.client.get(url)

    #         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_transformationledger_requests_bad_target_name(self):
    #     """Test that making a get request to the mappings api with all params
    #         fails when no transformationledger is found"""
    #     self.sourceSchema.save()
    #     self.targetSchema.save()
    #     self.mapping.save()
    #     url = (f"%s?sourceName={self.sourceSchema.schema_name}&"
    #            f"sourceVersion={self.sourceSchema.version}&"
    #            f"targetName=testtest") % (reverse('api:transformationledger'))
    #     response = self.client.get(url)
    #     responseDict = json.loads(response.content)
    #     expected_error = ["Error; no target schema found with the name "
    #                       "'testtest'"]
    #     self.assertEqual(responseDict['message'], expected_error)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_transformationledger_requests_all_params(self):
    #     """Test that making a get request to the mappings api with all params
    #         is returns transformationledger when it exists"""
    #     url = ("%s?sourceName=test_name&sourceVersion=1.2.3&"
    #            "targetName=test_name_1&" + "targetVersion=1.2.4") % (
    #         reverse('api:transformationledger'))
    #     self.sourceSchema.save()
    #     self.targetSchema.save()
    #     self.mapping.save()
    #     with patch('api.views.TermSet.objects') as mappingObj:
    #         mappingObj.return_value = mappingObj
    #         mappingObj.all.return_value = mappingObj
    #         mappingObj.filter.return_value = mappingObj
    #         mappingObj.first.side_effect = [
    #             self.sourceSchema, self.targetSchema]

    #         response = self.client.get(url)
    #         responseDict = json.loads(response.content)

    #         self.assertEqual(response.status_code, status.HTTP_200_OK)
    #         self.assertEqual(responseDict["schema_mapping"],
    #                          self.schema_mapping)

    # def test_transformationledger_requests_no_version(self):
    #     """Test that making a get request to the mappings api with no versions
    #         is returns transformationledger when it exists"""
    #     url = ("%s?sourceName=test_name&"
    #            "targetName=test_name_1") % (
    #         reverse('api:transformationledger'))
    #     self.sourceSchema.save()
    #     self.targetSchema.save()
    #     self.mapping.save()
    #     with patch('api.views.TermSet.objects') as mappingObj:
    #         mappingObj.return_value = mappingObj
    #         mappingObj.all.return_value = mappingObj
    #         mappingObj.filter.return_value = mappingObj
    #         mappingObj.first.side_effect = [
    #             self.sourceSchema, self.targetSchema]

    #         response = self.client.get(url)
    #         responseDict = json.loads(response.content)

    #         self.assertEqual(response.status_code, status.HTTP_200_OK)
    #         self.assertEqual(responseDict["schema_mapping"],
    #                          self.schema_mapping)

    # def test_transformationledger_requests_wrong_source_version(self):
    #     """Test that making a get request to the mappings api
    #         fails correctly when no mapping with source version exists"""
    #     self.sourceSchema.save()
    #     self.targetSchema.save()
    #     self.mapping.save()
    #     url = (f"%s?sourceName={self.sourceSchema.schema_name}&"
    #            "sourceVersion=0.0.0&"
    #            f"targetName={self.targetSchema.schema_name}&"
    #            f"targetVersion={self.targetSchema.version}") % (
    #         reverse('api:transformationledger'))
    #     response = self.client.get(url)
    #     responseDict = json.loads(response.content)
    #     expected_error = ["Error; no source schema found for version " +
    #                       "'0.0.0'"]
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(responseDict['message'], expected_error)

    # def test_transformationledger_requests_wrong_target_version(self):
    #     """Test that making a get request to the mappings api
    #         fails correctly when no mapping with target version exists"""
    #     self.sourceSchema.save()
    #     self.targetSchema.save()
    #     self.mapping.save()
    #     url = (f"%s?sourceName={self.sourceSchema.schema_name}&"
    #            f"sourceVersion={self.sourceSchema.version}&"
    #            f"targetName={self.targetSchema.schema_name}&"
    #            "targetVersion=0.0.0") % (
    #         reverse('api:transformationledger'))
    #     response = self.client.get(url)
    #     responseDict = json.loads(response.content)
    #     expected_error = ["Error; no target schema found for version " +
    #                       "'0.0.0'"]
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(responseDict['message'], expected_error)

    # def test_transformationledger_requests_iris(self):
    #     """Test that making a get request to the mappings api with iris
    #         returns transformationledger when it exists"""
    #     self.sourceSchema.save()
    #     self.targetSchema.save()
    #     self.mapping.save()
    #     url = (f"%s?sourceIRI={self.sourceSchema.schema_iri}&"
    #            f"targetIRI={self.targetSchema.schema_iri}") % (
    #         reverse('api:transformationledger'))
    #     with patch('api.views.TermSet.objects') as mappingObj:
    #         mappingObj.return_value = mappingObj
    #         mappingObj.all.return_value = mappingObj
    #         mappingObj.filter.return_value = mappingObj
    #         mappingObj.first.side_effect = [
    #             self.sourceSchema, self.targetSchema]

    #         response = self.client.get(url)
    #         responseDict = json.loads(response.content)

    #         self.assertEqual(response.status_code, status.HTTP_200_OK)
    #         self.assertEqual(responseDict["schema_mapping"],
    #                          self.schema_mapping)

    # def test_transformationledger_requests_iris_no_source(self):
    #     """Test that making a get request to the mappings api with iris
    #         fails correctly when no mapping with source exists"""
    #     self.sourceSchema.save()
    #     self.targetSchema.save()
    #     url = (f"%s?sourceIRI=badIRI&"
    #            f"targetIRI={self.targetSchema.schema_iri}") % (
    #         reverse('api:transformationledger'))
    #     response = self.client.get(url)
    #     responseDict = json.loads(response.content)
    #     expected_error = ["Error; no schema found with the iri " +
    #                       "'badIRI'"]
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(responseDict['message'], expected_error)

    # def test_transformationledger_requests_iris_no_target(self):
    #     """Test that making a get request to the mappings api with iris
    #         fails correctly when no mapping with target exists"""
    #     self.sourceSchema.save()
    #     self.targetSchema.save()
    #     self.mapping.save()
    #     url = (f"%s?sourceIRI={self.sourceSchema.schema_iri}&"
    #            f"targetIRI=testtest") % (
    #         reverse('api:transformationledger'))
    #     response = self.client.get(url)
    #     responseDict = json.loads(response.content)
    #     expected_error = ["Error; no schema found with the iri 'testtest'"]
    #     self.assertEqual(responseDict['message'], expected_error)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
