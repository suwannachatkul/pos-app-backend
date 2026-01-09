from typing import Any

import strawberry
from fastapi import Depends, Request
from strawberry.fastapi import GraphQLRouter
from strawberry.types import ExecutionContext

from config.database import AsyncSession, get_async_db
from shared.logging import logger

from .mutations import BaseMutation
from .payment.mutations import PaymentMutations
from .payment.queries import PaymentQueries
from .queries import BaseQuery


# Add more query/mutation classes here
DOMAIN_QUERY_CLASSES = [BaseQuery, PaymentQueries]
DOMAIN_MUTATION_CLASSES = [BaseMutation, PaymentMutations]


class BaseSchema(strawberry.Schema):
    """Custom Strawberry Schema to handle error logging"""

    def process_errors(
        self,
        errors: list[Exception],
        execution_context: ExecutionContext | None = None,
    ) -> None:
        for error in errors:
            # Log with full traceback
            logger.exception(
                f"GraphQL error: {error}",
                exc_info=error,
                extra={
                    "query": execution_context.query if execution_context else None,
                    "variables": execution_context.variables
                    if execution_context
                    else None,
                },
            )


# Create the GraphQL schema
schema = BaseSchema(
    query=strawberry.type(
        type("Query", tuple(DOMAIN_QUERY_CLASSES), {"__doc__": "Root Query"})
    ),
    mutation=strawberry.type(
        type("Mutation", tuple(DOMAIN_MUTATION_CLASSES), {"__doc__": "Root Mutation"})
    ),
)


# Context getter for GraphQL
async def get_context(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
) -> dict[str, Any]:
    """Provide context for GraphQL resolvers."""
    return {
        "request": request,
        "db": db,
    }


# Create the GraphQL router for FastAPI
def create_graphql_router() -> GraphQLRouter:
    return GraphQLRouter(schema, path="/graphql", context_getter=get_context)
