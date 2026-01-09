import strawberry


@strawberry.type
class BaseMutation:
    @strawberry.mutation
    def placeholder(self) -> str:
        """Placeholder mutation - replace with your actual mutations."""
        return "Mutation placeholder"
