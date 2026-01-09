import strawberry


@strawberry.type
class BaseQuery:
    @strawberry.field
    def health(self) -> str:
        """Health check query."""
        return "GraphQL API is running"
