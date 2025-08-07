# schema/schema.py
import graphene
from .queries.appointment import AppointmentQuery
from .queries.facility import FacilityQuery
from .queries.medication import MedicationQuery
from .queries.prescription import PrescriptionQuery
from .queries.user import UserQuery

from .mutations.appointment import AppointmentMutation
from .mutations.facility import FacilityMutation
from .mutations.medication import MedicationMutation
from .mutations.prescription import PrescriptionMutation
from .mutations.user import UserMutation

class Query(AppointmentQuery, FacilityQuery, MedicationQuery, PrescriptionQuery, UserQuery, graphene.ObjectType):
    pass

class Mutation(AppointmentMutation, FacilityMutation, MedicationMutation, PrescriptionMutation, UserMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)