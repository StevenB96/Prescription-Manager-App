# schema/queries/prescription.py
import graphene
from ..types import PrescriptionType
from ...models import Prescription

class PrescriptionQuery(graphene.ObjectType):
    prescription = graphene.Field(PrescriptionType, id=graphene.ID(required=True))
    all_prescriptions = graphene.List(PrescriptionType)

    def resolve_prescription(self, info, id):
        return Prescription.get(id)

    def resolve_all_prescriptions(self, info):
        return Prescription.list_all()
