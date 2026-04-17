"""
Test Runs API module

Example usage:

    >>> from py_jama_client.client import JamaClient
    >>> client = JamaClient(host=HOST, credentials=(USERNAME, PASSWORD))
    >>> test_runs_api = TestRunsAPI(client)
    >>> test_runs = test_runs_api.get_test_runs()
"""

import json
import logging

from py_jama_client.client import JamaClient
from py_jama_client.exceptions import APIException, CoreException
from py_jama_client.models import JamaTestRun, TestRunUpdateRequest
from py_jama_client.response import ClientResponse

py_jama_client_logger = logging.getLogger("py_jama_client")


class TestRunsAPI:
    client: JamaClient

    resource_path = "testruns"

    def __init__(self, client: JamaClient):
        self.client = client

    def put_test_run(
        self,
        test_run_id: int,
        data: "TestRunUpdateRequest | None" = None,
        *args,
        params: dict | None = None,
        **kwargs,
    ) -> "ClientResponse[JamaTestRun]":
        """
        Update a test run.

        Args:
            test_run_id: the api id of the test run to update
            data: request body with the fields to update (e.g. testRunStatus, actualResults)

        Returns:
            ClientResponse[JamaTestRun]: the updated test run
        """
        resource_path = f"testruns/{test_run_id}"
        headers = {"content-type": "application/json"}
        try:
            response = self.client.put(
                resource_path,
                params,
                data=json.dumps(data) if data is not None else None,
                headers=headers,
                **kwargs,
            )
        except CoreException as err:
            py_jama_client_logger.error(err)
            raise APIException(str(err))
        JamaClient.handle_response_status(response)
        return ClientResponse.from_response(response)
