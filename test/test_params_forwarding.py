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
