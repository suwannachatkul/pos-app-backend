"""Common GraphQL types shared across the API."""

import strawberry


@strawberry.type
class GraphQLError:
    """Standard error type for GraphQL responses."""

    code: str
    message: str
    details: str | None = None
