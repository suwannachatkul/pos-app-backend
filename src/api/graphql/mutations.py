import strawberry


@strawberry.type
class Mutation:
    @strawberry.mutation
    def placeholder(self) -> str:
        """Placeholder mutation - replace with your actual mutations."""
        return "Mutation placeholder"
