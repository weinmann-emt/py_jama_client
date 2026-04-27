"""
Domain model TypedDicts and enums for the Jama REST API.

These types describe the structure of items returned by the API. The `fields`
sub-dict on each item contains system fields defined here plus any
instance-specific custom fields (accessible as `str` keys).
"""

__all__ = [
    "ItemCategory",
    "TestRunStatus",
    "JamaItemLocation",
    "JamaItemLock",
    "AbstractItemFields",
    "TestCaseFields",
    "TestPlanFields",
    "TestCycleFields",
    "TestRunFields",
    "JamaAbstractItem",
    "JamaTestCase",
    "JamaTestPlan",
    "JamaTestCycle",
    "JamaTestRun",
    "TestRunUpdateFields",
    "TestRunUpdateRequest",
]

from enum import StrEnum
from typing import Any, NotRequired, TypedDict


class ItemCategory(StrEnum):
    ATTACHMENT = "ATTACHMENT"
    COMPONENT = "COMPONENT"
    CORE = "CORE"
    DEFECT = "DEFECT"
    SECTION = "SECTION"
    SET = "SET"
    TEST_CASE = "TEST_CASE"
    TEST_CYCLE = "TEST_CYCLE"
    TEST_PLAN = "TEST_PLAN"
    TEST_RUN = "TEST_RUN"
    TEXT = "TEXT"


class TestRunStatus(StrEnum):
    NOT_RUN = "NOT_RUN"
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    INPROGRESS = "INPROGRESS"


# ---------------------------------------------------------------------------
# Structural sub-types
# ---------------------------------------------------------------------------

class _JamaItemParent(TypedDict, total=False):
    item: int | None
    project: int


class JamaItemLocation(TypedDict, total=False):
    sequence: str
    depth: int
    globalSortOrder: int
    parent: _JamaItemParent
    sortOrder: int


class JamaItemLock(TypedDict, total=False):
    locked: bool
    lastLockedDate: str | None
    lockedBy: int | None


# ---------------------------------------------------------------------------
# Fields sub-dicts (one per item category)
# ---------------------------------------------------------------------------

class AbstractItemFields(TypedDict, total=False):
    """Base fields present on most abstract items (requirements, components, etc.)."""
    documentKey: str
    globalId: str
    name: str
    description: str
    project: int


class TestCaseFields(TypedDict, total=False):
    """Fields for items with category TEST_CASE."""
    documentKey: str
    globalId: str
    name: str
    description: str
    status: str
    priority: str
    assignedTo: int
    testCaseSteps: list[dict[str, Any]]
    testCaseStatus: str
    testRunResults: Any


class TestPlanFields(TypedDict, total=False):
    """Fields for items with category TEST_PLAN."""
    documentKey: str
    globalId: str
    name: str
    description: str
    project: int
    workflow_status: NotRequired[str]


class TestCycleFields(TypedDict, total=False):
    """Fields for items with category TEST_CYCLE."""
    documentKey: str
    globalId: str
    name: str
    description: str
    project: int
    testPlan: int
    startDate: str
    endDate: str


class TestRunFields(TypedDict, total=False):
    """Fields for items with category TEST_RUN."""
    documentKey: str
    globalId: str
    name: str
    description: str
    testPlan: int
    testCycle: int
    testRunSetName: str
    testCase: int
    testRunSteps: list[dict[str, Any]]
    actualResults: str
    assignedTo: int
    modifiedDate: str
    duration: str
    testRunStatus: TestRunStatus
    workflow_status: str
    executionDate: str # ISO8601 date string


# ---------------------------------------------------------------------------
# Top-level item TypedDicts
# ---------------------------------------------------------------------------

class _JamaItemBaseRequired(TypedDict, total=True):
    id: int
    documentKey: str
    globalId: str
    itemType: int
    project: int


class _JamaItemBase(_JamaItemBaseRequired, total=False):
    childItemType: int | None
    createdDate: str
    modifiedDate: str
    lastActivityDate: str
    createdBy: int
    modifiedBy: int
    location: JamaItemLocation
    lock: JamaItemLock
    type: str
    resources: dict[str, Any]


class JamaAbstractItem(_JamaItemBase, total=False):
    """An item returned from the /abstractitems endpoint (requirements, components, etc.)."""
    fields: AbstractItemFields


class JamaTestCase(_JamaItemBase, total=False):
    """An item with category TEST_CASE."""
    fields: TestCaseFields


class JamaTestPlan(_JamaItemBase, total=False):
    """An item with category TEST_PLAN."""
    fields: TestPlanFields


class JamaTestCycle(_JamaItemBase, total=False):
    """An item with category TEST_CYCLE."""
    fields: TestCycleFields


class JamaTestRun(_JamaItemBase, total=False):
    """An item with category TEST_RUN."""
    fields: TestRunFields


# ---------------------------------------------------------------------------
# Request body types
# ---------------------------------------------------------------------------

class TestRunUpdateFields(TypedDict, total=False):
    """Writable fields for PUT /testruns/{id}."""
    testRunStatus: TestRunStatus
    actualResults: str
    assignedTo: int
    description: str


class TestRunUpdateRequest(TypedDict):
    """Request body for put_test_run()."""
    fields: TestRunUpdateFields
