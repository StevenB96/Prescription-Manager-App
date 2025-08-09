# prescription_manager_app\prescription_manager_app\schema\queries\user.py

import graphene
from ..types import UserType
from ...models import User

class UserQuery(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.ID(required=True))
    all_users = graphene.List(UserType)

    def resolve_user(self, info, id):
        return User.get(id)

    def resolve_all_users(self, info):
        return User.list_all()
