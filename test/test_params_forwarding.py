import json
from unittest.mock import MagicMock

import pytest
from py_jama_client.apis.items_api import ItemsAPI
from py_jama_client.apis.relationships_api import RelationshipsAPI
from py_jama_client.constants import DEFAULT_ALLOWED_RESULTS_PER_PAGE


@pytest.mark.parametrize(
    "api_class, method, args, resource_path",
    [
        (ItemsAPI, "get_items_synceditems", (1,), "items/1/synceditems"),
        (ItemsAPI, "get_items_downstream_relationships", (1,), "items/1/downstreamrelationships"),
        (RelationshipsAPI, "get_relationship_types", (), "relationshiptypes/"),
    ],
)
def test_params_and_kwargs_are_forwarded(api_class, method, args, resource_path):
    client = MagicMock()
    params = {"include": "data.project"}

    getattr(api_class(client), method)(*args, params=params, timeout=5)

    client.get_all.assert_called_once_with(
        resource_path,
        params,
        allowed_results_per_page=DEFAULT_ALLOWED_RESULTS_PER_PAGE,
        timeout=5,
    )


@pytest.mark.parametrize("last_id_required", [False, True])
def test_get_relationships_forwards_kwargs_to_paged_reads(last_id_required):
    client = MagicMock()
    probe = client.get.return_value
    probe.status_code = 400 if last_id_required else 200
    probe.text = "lastId parameter is now required" if last_id_required else ""
    api = RelationshipsAPI(client)
    api.get_all_lastid = MagicMock()

    api.get_relationships(1, timeout=5)

    paged_read = api.get_all_lastid if last_id_required else client.get_all
    paged_read.assert_called_once_with(
        "relationships",
        {"project": 1},
        allowed_results_per_page=DEFAULT_ALLOWED_RESULTS_PER_PAGE,
        timeout=5,
    )


def test_post_item_sync_works_without_params():
    client = MagicMock()
    client.post.return_value.status_code = 201
    client.post.return_value.json.return_value = {"meta": {"id": 2}, "links": {}, "linked": {}, "data": {}}

    ItemsAPI(client).post_item_sync(source_item=2, pool_item=1)

    args, kwargs = client.post.call_args
    assert args == ("items/1/synceditems", None)
    assert json.loads(kwargs["data"]) == {"item": 2}


def test_post_item_sends_string_global_id():
    client = MagicMock()
    client.post.return_value.status_code = 201
    client.post.return_value.json.return_value = {"meta": {"id": 3}, "links": {}, "linked": {}, "data": {}}

    ItemsAPI(client).post_item(1, 2, 0, {"project": 1}, {"name": "x"}, global_id="GID-42")

    args, kwargs = client.post.call_args
    assert args[1] == {"setGlobalIdManually": True}
    assert json.loads(kwargs["data"])["globalId"] == "GID-42"
