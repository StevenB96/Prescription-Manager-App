# schema/mutations/prescription.py
import graphene
from ..types import PrescriptionType
from ...models import Prescription

class CreatePrescription(graphene.Mutation):
    prescription = graphene.Field(PrescriptionType)

    class Arguments:
        pharmacy_id = graphene.ID(required=True)
        medication_id = graphene.ID(required=True)
        prescriber_id = graphene.ID()
        patient_id = graphene.ID(required=True)
        medical_exemption_type = graphene.Int()
        status = graphene.Int()

    def mutate(self, info, pharmacy_id, medication_id, patient_id, prescriber_id=None, medical_exemption_type=Prescription.EXEMPTION_NONE, status=Prescription.STATUS_NEW):
        presc = Prescription.create(
            pharmacy_id=pharmacy_id,
            medication_id=medication_id,
            prescriber_id=prescriber_id,
            patient_id=patient_id,
            medical_exemption_type=medical_exemption_type,
            status=status
        )
        return CreatePrescription(prescription=presc)

class UpdatePrescription(graphene.Mutation):
    prescription = graphene.Field(PrescriptionType)

    class Arguments:
        id = graphene.ID(required=True)
        pharmacy_id = graphene.ID()
        medication_id = graphene.ID()
        prescriber_id = graphene.ID()
        patient_id = graphene.ID()
        medical_exemption_type = graphene.Int()
        status = graphene.Int()

    def mutate(self, info, id, **kwargs):
        presc = Prescription.update(id, **kwargs)
        return UpdatePrescription(prescription=presc)

class DeletePrescription(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        success = Prescription.delete(id)
        return DeletePrescription(ok=success)

class PrescriptionMutation(graphene.ObjectType):
    create_prescription = CreatePrescription.Field()
    update_prescription = UpdatePrescription.Field()
    delete_prescription = DeletePrescription.Field()