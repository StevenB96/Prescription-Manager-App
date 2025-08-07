# schema/queries/medication.py
import graphene
from ..types import MedicationType
from ...models import Medication

class MedicationQuery(graphene.ObjectType):
    medication = graphene.Field(MedicationType, id=graphene.ID(required=True))
    all_medications = graphene.List(MedicationType)

    def resolve_medication(self, info, id):
        return Medication.get(id)

    def resolve_all_medications(self, info):
        return Medication.list_all()
