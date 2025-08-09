# prescription_manager_app\prescription_manager_app\schema\types.py

import graphene

class AppointmentType(graphene.ObjectType):
    id = graphene.ID()
    surgery_id = graphene.ID()
    medical_professional_id = graphene.ID()
    patient_id = graphene.ID()
    time = graphene.DateTime()
    status = graphene.Int()
    status_display = graphene.String()
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()

    def resolve_status_display(self, info):
        return self.get_status_display()

class FacilityType(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    address = graphene.String()
    type = graphene.Int()
    type_display = graphene.String()
    status = graphene.Int()
    status_display = graphene.String()
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()

    def resolve_type_display(self, info):
        return self.get_type_display()

    def resolve_status_display(self, info):
        return self.get_status_display()

class MedicationType(graphene.ObjectType):
    id = graphene.ID()
    generic_name = graphene.String()
    brand_name = graphene.String()
    chemical_name = graphene.String()
    price = graphene.Float()
    status = graphene.Int()
    status_display = graphene.String()
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()

    def resolve_status_display(self, info):
        return self.get_status_display()

class PrescriptionType(graphene.ObjectType):
    id = graphene.ID()
    pharmacy_id = graphene.ID()
    medication_id = graphene.ID()
    prescriber_id = graphene.ID()
    patient_id = graphene.ID()
    medical_exemption_type = graphene.Int()
    medical_exemption_display = graphene.String()
    status = graphene.Int()
    status_display = graphene.String()
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()

    def resolve_medical_exemption_display(self, info):
        return self.get_exemption_display()

    def resolve_status_display(self, info):
        return self.get_status_display()

class UserType(graphene.ObjectType):
    id = graphene.ID()
    username = graphene.String()
    email = graphene.String()
    password_hash = graphene.String()
    role = graphene.Int()
    role_display = graphene.String()
    status = graphene.Int()
    status_display = graphene.String()
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()

    def resolve_role_display(self, info):
        return self.get_role_display()

    def resolve_status_display(self, info):
        return self.get_status_display()
