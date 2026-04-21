"""
Test Plans API module

Example usage:

    >>> from py_jama_client.client import JamaClient
    >>> client = JamaClient(host=HOST, credentials=(USERNAME, PASSWORD))
    >>> test_plans_api = TestPlansAPI(client)
    >>> test_plans = test_plans_api.get_test_plans()
"""

import json
import logging

from py_jama_client.client import JamaClient
from py_jama_client.constants import DEFAULT_ALLOWED_RESULTS_PER_PAGE
from py_jama_client.exceptions import APIException, CoreException
from py_jama_client.response import ClientResponse

py_jama_client_logger = logging.getLogger("py_jama_client")


class TestPlansAPI:
    client: JamaClient

    resource_path = "testplans"

    def __init__(self, client: JamaClient):
        self.client = client

    def get_testplans(
        self,
        project_id: int,
        *args,
        params: dict | None = None,
        allowed_results_per_page=DEFAULT_ALLOWED_RESULTS_PER_PAGE,
        **kwargs,
    ):
        """
        Get all test plans in the project with the specified ID.

        Args:
            project_id (int): The API id of the project.

        Returns:
            ClientResponse: List of test plans.
        """
        req_params = {"project": project_id}
        if params is None:
            params = req_params
        else:
            params.update(req_params)
        return self.client.get_all(
            self.resource_path,
            params,
            allowed_results_per_page=allowed_results_per_page,
            **kwargs,
        )

    def post_testplans_testcycles(
        self,
        testplan_id: int,
        testcycle_name: str,
        start_date: str,
        end_date: str,
        testgroups_to_include: list[int] | None = None,
        testrun_status_to_include: list[str] | None = None,
        *args,
        params: dict | None = None,
        **kwargs,
    ):
        """
        This method will create a new Test Cycle.

        Args:
            testplan_id (int): The API_ID of the testplan to create the test
                cycle from.
            testcycle_name (str): The name you would like to set for the new
                Test Cycle
            start_date (str): Start date in 'yyyy-mm-dd' Format
            end_date (str): End date in 'yyyy-mm-dd' Format
            testgroups_to_include (int[]):  This array of integers specify the
                test groups to be included.
            testrun_status_to_include (str[]): Only valid after generating the
                first Test Cycle, you may choose to only generate Test Runs
                that were a specified status in the previous cycle. Do not
                specify anything to include all statuses

        Returns:
            (int): Returns the the newly created testcycle
        """
        resource_path = f"testplans/{testplan_id}/testcycles"
        headers = {"content-type": "application/json"}
        fields = {"name": testcycle_name, "startDate": start_date, "endDate": end_date}
        test_run_gen_config: dict = {}
        if testgroups_to_include is not None:
            test_run_gen_config["testGroupsToInclude"] = testgroups_to_include
        if testrun_status_to_include is not None:
            test_run_gen_config["testRunStatusesToInclude"] = testrun_status_to_include
        body = {"fields": fields, "testRunGenerationConfig": test_run_gen_config}

        # Make the API Call
        try:
            response = self.client.post(
                resource_path,
                params,
                data=json.dumps(body),
                headers=headers,
                **kwargs,
            )
        except CoreException as err:
            py_jama_client_logger.error(err)
            raise APIException(str(err))

        # Validate response
        JamaClient.handle_response_status(response)
        return ClientResponse.from_response(response)

    def get_testplans_testgroups(
        self,
        testplan_id: int,
        *args,
        params: dict | None = None,
        allowed_results_per_page=DEFAULT_ALLOWED_RESULTS_PER_PAGE,
        **kwargs,
    ):
        """
        Returns all test groups for the test plan with the specified id.

        Args:
            testplan_id (int): The API id of the test plan.

        Returns:
            ClientResponse: A Json array of test group objects.
        """
        resource_path = f"testplans/{testplan_id}/testgroups"
        return self.client.get_all(
            resource_path,
            params,
            allowed_results_per_page=allowed_results_per_page,
            **kwargs,
        )
    
    def get_testplans_testgroup(
        self,
        testplan_id: int,
        testgroup_id: int,
        *args,
        params: dict | None = None,
        **kwargs,
    ):
        """
        Returns the test group with the specified ID.

        Args:
            testplan_id (int): The API id of the test plan.
            testgroup_id (int): The API id of the test group.

        Returns:
            ClientResponse: A dictionary object representing the test group.
        """
        resource_path = f"testplans/{testplan_id}/testgroups/{testgroup_id}"
        try:
            response = self.client.get(resource_path, params, **kwargs)
        except CoreException as err:
            py_jama_client_logger.error(err)
            raise APIException(str(err))
        JamaClient.handle_response_status(response)
        return ClientResponse.from_response(response)


    def post_testplans_testgroups(
        self,
        testplan_id: int,
        name: str,
        *args,
        params: dict | None = None,
        **kwargs,
    ):
        """
        Creates a new test group in the test plan with the specified id.

        Args:
            testplan_id (int): The API id of the test plan.
            name (str): The name of the new test group.

        Returns:
            ClientResponse: The newly created test group.
        """
        resource_path = f"testplans/{testplan_id}/testgroups"
        body = {"name": name}
        headers = {"content-type": "application/json"}
        try:
            response = self.client.post(
                resource_path,
                params,
                data=json.dumps(body),
                headers=headers,
                **kwargs,
            )
        except CoreException as err:
            py_jama_client_logger.error(err)
            raise APIException(str(err))
        JamaClient.handle_response_status(response)
        return ClientResponse.from_response(response)

    def get_testplans_testgroups_testcases(
        self,
        testplan_id: int,
        testgroup_id: int,
        *args,
        params: dict | None = None,
        allowed_results_per_page=DEFAULT_ALLOWED_RESULTS_PER_PAGE,
        **kwargs,
    ):
        """
        Returns all test cases for the test group with the specified id.

        Args:
            testplan_id (int): The API id of the test plan.
            testgroup_id (int): The API id of the test group.

        Returns:
            ClientResponse: List of test cases in the test group.
        """
        resource_path = f"testplans/{testplan_id}/testgroups/{testgroup_id}/testcases"
        return self.client.get_all(
            resource_path,
            params,
            allowed_results_per_page=allowed_results_per_page,
            **kwargs,
        )
    
    def get_testplans_testgroups_testcase(
        self,
        testplan_id: int,
        testgroup_id: int,
        testcase_id: int,
        *args,
        params: dict | None = None,
        **kwargs,
    ):
        """
        Returns the test case with the specified ID from the test group.

        Args:
            testplan_id (int): The API id of the test plan.
            testgroup_id (int): The API id of the test group.
            testcase_id (int): The API id of the test case.

        Returns:
            ClientResponse: The test case.
        """
        resource_path = f"testplans/{testplan_id}/testgroups/{testgroup_id}/testcases/{testcase_id}"
        try:
            response = self.client.get(resource_path, params, **kwargs)
        except CoreException as err:
            py_jama_client_logger.error(err)
            raise APIException(str(err))
        JamaClient.handle_response_status(response)
        return ClientResponse.from_response(response)


    def post_testplans_testgroups_testcases(
        self,
        testplan_id: int,
        testgroup_id: int,
        testcase_id: int,
        *args,
        params: dict | None = None,
        **kwargs,
    ):
        """
        Adds a test case to the test group with the specified id.

        Args:
            testplan_id (int): The API id of the test plan.
            testgroup_id (int): The API id of the test group.
            testcase_id (int): The API id of the test case item to add.

        Returns:
            ClientResponse: The newly added test case entry.
        """
        resource_path = f"testplans/{testplan_id}/testgroups/{testgroup_id}/testcases"
        body = {"testCase": testcase_id}
        headers = {"content-type": "application/json"}
        try:
            response = self.client.post(
                resource_path,
                params,
                data=json.dumps(body),
                headers=headers,
                **kwargs,
            )
        except CoreException as err:
            py_jama_client_logger.error(err)
            raise APIException(str(err))
        JamaClient.handle_response_status(response)
        return ClientResponse.from_response(response)
