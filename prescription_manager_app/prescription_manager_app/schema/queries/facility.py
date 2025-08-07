# schema/queries/facility.py
import graphene
from ..types import FacilityType
from ...models import Facility

class FacilityQuery(graphene.ObjectType):
    facility = graphene.Field(FacilityType, id=graphene.ID(required=True))
    all_facilities = graphene.List(FacilityType)

    def resolve_facility(self, info, id):
        return Facility.get(id)

    def resolve_all_facilities(self, info):
        return Facility.list_all()
