__all__ = ["ClientResponse"]

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from httpx import Response

T = TypeVar("T")


@dataclass
class ClientResponse(Generic[T]):
    meta: dict[str, Any]
    links: dict[str, Any]
    linked: dict[str, Any]
    data: T

    @classmethod
    def from_response(cls, response: Response) -> "ClientResponse[Any]":
        """
        Parse a response from the Jama API into a ClientResponse object.

        Args:
            response (httpx.Response): The response from the Jama API.

        Returns:
            ClientResponse: A ClientResponse object.
        """
        response_json: dict = response.json()

        return ClientResponse(
            meta=response_json.get("meta", {}),
            links=response_json.get("links", {}),
            linked=response_json.get("linked", {}),
            data=response_json.get("data", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert client response object to dictionary."""
        return {
            "meta": self.meta,
            "links": self.links,
            "linked": self.linked,
            "data": self.data,
        }

    def __add__(self, other: "ClientResponse[T]") -> "ClientResponse[T]":
        self.meta.update(other.meta)
        self.links.update(other.links)
        self.linked.update(other.linked)
        self.data += other.data  # type: ignore[operator]
        return self
