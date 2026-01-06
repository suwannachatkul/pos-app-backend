import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        """A simple hello world query."""
        return "Hello from GraphQL!"

    @strawberry.field
    def health(self) -> str:
        """Health check query."""
        return "GraphQL API is running"
