import strawberry
from strawberry.fastapi import GraphQLRouter

from .mutations import Mutation
from .queries import Query


# Create the main GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)


# Create the GraphQL router for FastAPI
def create_graphql_router() -> GraphQLRouter:
    return GraphQLRouter(schema, path="/graphql")
