"""Offline tests for retrying throttled (HTTP 429) requests."""

import functools
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime
from unittest.mock import call, patch

import httpx
import pytest

from py_jama_client.client import JamaClient, retry_after_seconds
from py_jama_client.constants import DEFAULT_RETRY_BACKOFF
from py_jama_client.exceptions import TooManyRequestsException


def _client(*statuses, headers=None, **kwargs):
    """A client whose transport answers with ``statuses`` in order (the last one
    repeats); returns it with the list of requests sent."""
    sent = []

    def handler(request):
        status = statuses[min(len(sent), len(statuses) - 1)]
        sent.append(request)
        return httpx.Response(
            status, headers=headers if status == 429 else None, json={"data": []}
        )

    class _MockedClient(JamaClient):
        session_class = staticmethod(
            functools.partial(httpx.Client, transport=httpx.MockTransport(handler))
        )

    return _MockedClient("https://jama.example", **kwargs), sent


@pytest.fixture
def sleep():
    """Patch out the backoff sleep and its jitter; yields the sleep mock."""
    with (
        patch("py_jama_client.client.time.sleep") as sleep,
        patch("py_jama_client.client.random.uniform", return_value=0.0),
    ):
        yield sleep


def test_throttled_request_is_retried_until_it_succeeds(sleep):
    client, sent = _client(429, 429, 200)

    response = client.get("items")

    assert response.status_code == 200
    assert len(sent) == 3
    assert sleep.call_args_list == [call(3.0), call(5.0)]


def test_backoff_adds_jitter():
    client, _ = _client(429, 200)
    with (
        patch("py_jama_client.client.time.sleep") as sleep,
        patch("py_jama_client.client.random.uniform", return_value=0.5) as jitter,
    ):
        client.get("items")

    sleep.assert_called_once_with(3.5)
    jitter.assert_called_once_with(0.0, 1.0)


def test_persistent_429_is_returned_after_jamas_backoff_schedule(sleep):
    client, sent = _client(429)

    response = client.get("items")

    assert response.status_code == 429
    assert len(sent) == len(DEFAULT_RETRY_BACKOFF) + 1
    assert sleep.call_args_list == [call(step) for step in DEFAULT_RETRY_BACKOFF]
    with pytest.raises(TooManyRequestsException) as exc_info:
        JamaClient.handle_response_status(response)
    assert exc_info.value.retry_after is None


def test_get_page_raises_once_retries_are_exhausted(sleep):
    client, _ = _client(429, headers={"Retry-After": "2"})

    with pytest.raises(TooManyRequestsException) as exc_info:
        client.get_page("items", 0)

    assert exc_info.value.retry_after == 2.0


def test_retry_after_replaces_the_backoff_step(sleep):
    client, _ = _client(429, 200, headers={"Retry-After": "2"})

    client.get("items")

    sleep.assert_called_once_with(2.0)


def test_retry_after_beyond_the_longest_step_is_not_waited_for(sleep):
    client, sent = _client(429, 200, headers={"Retry-After": "60"})

    response = client.get("items")

    assert response.status_code == 429
    assert len(sent) == 1
    sleep.assert_not_called()


def test_custom_backoff_schedule(sleep):
    client, sent = _client(429, retry_backoff=(1.0,))

    assert client.get("items").status_code == 429
    assert len(sent) == 2
    sleep.assert_called_once_with(1.0)


def test_empty_backoff_disables_retries(sleep):
    client, sent = _client(429, retry_backoff=())

    assert client.get("items").status_code == 429
    assert len(sent) == 1
    sleep.assert_not_called()


@pytest.mark.parametrize("status", [200, 400, 404, 500])
def test_other_statuses_are_not_retried(sleep, status):
    client, sent = _client(status)

    assert client.get("items").status_code == status
    assert len(sent) == 1
    sleep.assert_not_called()


def test_retry_resends_method_params_and_body(sleep):
    client, sent = _client(429, 201)

    client.post("items", params={"a": "1"}, json={"name": "x"})

    assert [(r.method, str(r.url), r.content) for r in sent] == [
        ("POST", "https://jama.example/rest/v1/items?a=1", b'{"name":"x"}')
    ] * 2


@pytest.mark.parametrize(
    "body, reason",
    [
        (b'{"meta": {"message": "Slow down"}}', "Slow down"),
        (b'{"message": "Too Many Requests"}', "No Response"),
        (b"[]", "No Response"),
        (b"<html>Too Many Requests</html>", "No Response"),
    ],
)
def test_429_raises_too_many_requests_whatever_the_body(body, reason):
    response = httpx.Response(429, headers={"Retry-After": "5"}, content=body)

    with pytest.raises(TooManyRequestsException) as exc_info:
        JamaClient.handle_response_status(response)

    assert (exc_info.value.reason, exc_info.value.retry_after) == (reason, 5.0)


@pytest.mark.parametrize(
    "value, expected",
    [(None, None), ("", None), ("7", 7.0), ("1.5", 1.5), ("-3", 0.0), ("soon", None)],
)
def test_retry_after_seconds(value, expected):
    headers = {} if value is None else {"Retry-After": value}
    assert retry_after_seconds(httpx.Response(429, headers=headers)) == expected


def test_retry_after_http_date_is_converted_to_seconds():
    when = datetime.now(UTC) + timedelta(seconds=30)
    headers = {"Retry-After": format_datetime(when, usegmt=True)}

    seconds = retry_after_seconds(httpx.Response(429, headers=headers))

    assert seconds is not None and 25 <= seconds <= 30
