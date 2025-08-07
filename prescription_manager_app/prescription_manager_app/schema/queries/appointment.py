# schema/queries/appointment.py
import graphene
from ..types import AppointmentType
from ...models import Appointment

class AppointmentQuery(graphene.ObjectType):
    appointment = graphene.Field(AppointmentType, id=graphene.ID(required=True))
    all_appointments = graphene.List(AppointmentType)

    def resolve_appointment(self, info, id):
        return Appointment.get(id)

    def resolve_all_appointments(self, info):
        return Appointment.list_all()