# prescription_manager_app\prescription_manager_app\schema\mutations\appointment.py

import graphene
from ..types import AppointmentType
from ...models import Appointment

class CreateAppointment(graphene.Mutation):
    appointment = graphene.Field(AppointmentType)

    class Arguments:
        surgery_id = graphene.ID(required=True)
        medical_professional_id = graphene.ID()
        patient_id = graphene.ID(required=True)
        time = graphene.DateTime(required=True)
        status = graphene.Int()

    def mutate(self, info, surgery_id, patient_id, time, medical_professional_id=None, status=Appointment.STATUS_SCHEDULED):
        appt = Appointment.create(
            surgery_id=surgery_id,
            medical_professional_id=medical_professional_id,
            patient_id=patient_id,
            time=time,
            status=status
        )
        return CreateAppointment(appointment=appt)

class UpdateAppointment(graphene.Mutation):
    appointment = graphene.Field(AppointmentType)

    class Arguments:
        id = graphene.ID(required=True)
        surgery_id = graphene.ID()
        medical_professional_id = graphene.ID()
        patient_id = graphene.ID()
        time = graphene.DateTime()
        status = graphene.Int()

    def mutate(self, info, id, **kwargs):
        appt = Appointment.update(id, **kwargs)
        return UpdateAppointment(appointment=appt)

class DeleteAppointment(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        success = Appointment.delete(id)
        return DeleteAppointment(ok=success)

class AppointmentMutation(graphene.ObjectType):
    create_appointment = CreateAppointment.Field()
    update_appointment = UpdateAppointment.Field()
    delete_appointment = DeleteAppointment.Field()