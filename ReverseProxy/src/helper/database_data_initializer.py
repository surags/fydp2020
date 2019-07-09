from src.helper.database_intializer_helper import db
from src.model.application import Application
from src.model.application_permissions import ApplicationPermission
from src.model.os_container import OSContainer
from src.model.school import School
from src.model.user_type import UserType


class DatabaseDataInitializer:

    def __init__(self):
        self.write_data()

    def write_data(self):
        data1 = [(12345, '172.18.0.2', True, True)]

        data2 = ["Student",
                 "Teacher"]
        data3 = [(10, "City High School"),
                 (50, "University of Waterloo")]

        data4 = [(9, 26),
                 (9, 28)]

        data5 = [(1, "firefox"),
                 (25, "Microsoft Word"),
                 (26, "Notepad ++"),
                 (27, "Google Chrome"),
                 (28, "Borderlands 2")]

        with db.atomic():
            OSContainer.insert_many(data1, fields=[OSContainer.docker_container_id, OSContainer.ip_address, OSContainer.is_free, OSContainer.is_running]).execute()
            UserType.insert_many(data2, fields=[UserType.user_type]).execute()
            School.insert_many(data3, fields=[School.school_id, School.school_name]).execute()
            ApplicationPermission.insert_many(data4, fields=[ApplicationPermission.user_id,
                                                             ApplicationPermission.application_id]).execute()
            Application.insert_many(data5, fields=[Application.application_id, Application.application_name]).execute()
