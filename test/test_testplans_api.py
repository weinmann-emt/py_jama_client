import pytest

from py_jama_client.apis.test_plans_api import TestPlansAPI


@pytest.fixture(scope="function")
def test_plans_api(get_test_jama_client) -> TestPlansAPI:
    return TestPlansAPI(get_test_jama_client)


def test_get_testplans(test_plans_api, real_project):
    response = test_plans_api.get_testplans(project_id=real_project)
    assert response.data is not None


def test_get_testplans_testgroups(test_plans_api, real_test_plan):
    response = test_plans_api.get_testplans_testgroups(testplan_id=real_test_plan)
    assert response.data is not None


def test_get_testplans_testgroup(test_plans_api, real_test_plan, real_test_group):
    response = test_plans_api.get_testplans_testgroup(
        testplan_id=real_test_plan, testgroup_id=real_test_group
    )
    assert response.data is not None


def test_get_testplans_testgroups_testcases(
    test_plans_api, real_test_plan, real_test_group
):
    response = test_plans_api.get_testplans_testgroups_testcases(
        testplan_id=real_test_plan, testgroup_id=real_test_group
    )
    assert response.data is not None


def test_get_testplans_testgroups_testcase(
    test_plans_api, real_test_plan, real_test_group, real_test_group_testcase
):
    response = test_plans_api.get_testplans_testgroups_testcase(
        testplan_id=real_test_plan,
        testgroup_id=real_test_group,
        testcase_id=real_test_group_testcase,
    )
    assert response.data is not None
