# schema/mutations/medication.py
import graphene
from ..types import MedicationType
from ...models import Medication

class CreateMedication(graphene.Mutation):
    medication = graphene.Field(MedicationType)

    class Arguments:
        generic_name = graphene.String(required=True)
        brand_name = graphene.String()
        chemical_name = graphene.String()
        price = graphene.Float()
        status = graphene.Int()

    def mutate(self, info, generic_name, brand_name=None, chemical_name=None, price=0, status=Medication.STATUS_ACTIVE):
        med = Medication.create(
            generic_name=generic_name,
            brand_name=brand_name,
            chemical_name=chemical_name,
            price=price,
            status=status
        )
        return CreateMedication(medication=med)

class UpdateMedication(graphene.Mutation):
    medication = graphene.Field(MedicationType)

    class Arguments:
        id = graphene.ID(required=True)
        generic_name = graphene.String()
        brand_name = graphene.String()
        chemical_name = graphene.String()
        price = graphene.Float()
        status = graphene.Int()

    def mutate(self, info, id, **kwargs):
        med = Medication.update(id, **kwargs)
        return UpdateMedication(medication=med)

class DeleteMedication(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        success = Medication.delete(id)
        return DeleteMedication(ok=success)

class MedicationMutation(graphene.ObjectType):
    create_medication = CreateMedication.Field()
    update_medication = UpdateMedication.Field()
    delete_medication = DeleteMedication.Field()