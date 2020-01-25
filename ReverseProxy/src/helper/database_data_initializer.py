from src.model.base_model import db
from src.model.application import Application
from src.model.application_permissions import ApplicationPermission
from src.model.os_container import OSContainer
from src.model.school import School
from src.model.user_type import UserType


class DatabaseDataInitializer:

    def __init__(self):
        self.write_data()

    def write_data(self):
        try:
            data2 = [(1, 'Student'), (2, 'Teacher')]

            data3 = [(10, 'City High School'), (50, 'University of Waterloo')]

            data5 = [(1, 'firefox'),
                     (2, 'streamingos-teacher-portal'),
                     (25, 'Microsoft Word'),
                     (26, 'Notepad ++'),
                     (27, 'Google Chrome'),
                     (28, 'Borderlands 2')]

            with db.atomic():
                UserType.insert_many(data2, fields=['id', UserType.user_type]).execute()
                School.insert_many(data3, fields=[School.school_id, School.school_name]).execute()
                Application.insert_many(data5, fields=[Application.application_id, Application.application_name]).execute()
        except Exception:
            pass

