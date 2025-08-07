# schema/mutations/user.py
import graphene
from ..types import UserType
from ...models import User

class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password_hash = graphene.String(required=True)
        role = graphene.Int(required=True)
        status = graphene.Int()

    def mutate(self, info, username, email, password_hash, role, status=User.STATUS_ACTIVE):
        user = User.create(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            status=status
        )
        return CreateUser(user=user)

class UpdateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        id = graphene.ID(required=True)
        username = graphene.String()
        email = graphene.String()
        password_hash = graphene.String()
        role = graphene.Int()
        status = graphene.Int()

    def mutate(self, info, id, **kwargs):
        user = User.update(id, **kwargs)
        return UpdateUser(user=user)

class DeleteUser(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        success = User.delete(id)
        return DeleteUser(ok=success)

class UserMutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()