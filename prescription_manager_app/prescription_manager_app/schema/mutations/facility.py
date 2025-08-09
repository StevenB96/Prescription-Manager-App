# prescription_manager_app\prescription_manager_app\schema\mutations\facility.py

import graphene
from ..types import FacilityType
from ...models import Facility

class CreateFacility(graphene.Mutation):
    facility = graphene.Field(FacilityType)

    class Arguments:
        name = graphene.String(required=True)
        address = graphene.String(required=True)
        type = graphene.Int(required=True)
        status = graphene.Int()

    def mutate(self, info, name, address, type, status=Facility.STATUS_ACTIVE):
        facility = Facility.create(name=name, address=address, type=type, status=status)
        return CreateFacility(facility=facility)

class UpdateFacility(graphene.Mutation):
    facility = graphene.Field(FacilityType)

    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        address = graphene.String()
        type = graphene.Int()
        status = graphene.Int()

    def mutate(self, info, id, **kwargs):
        facility = Facility.update(id, **kwargs)
        return UpdateFacility(facility=facility)

class DeleteFacility(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        success = Facility.delete(id)
        return DeleteFacility(ok=success)

class FacilityMutation(graphene.ObjectType):
    create_facility = CreateFacility.Field()
    update_facility = UpdateFacility.Field()
    delete_facility = DeleteFacility.Field()