import graphene

class Query(graphene.ObjectType):
    hello: str = graphene.String(default_value="Hello")

schema = graphene.Schema(query=Query)