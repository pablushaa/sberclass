import requests

LOGIN_PAGE_URL = "https://auth.sberclass.ru/auth/realms/EduPowerKeycloak/protocol/openid-connect/auth?response_type=code&client_id=edupower&scope=openid%20profile%20email&redirect_uri=https://newschool.sberclass.ru/services/auth/login/oauth2/code/edupower?returnTo%3Dhttps://newschool.sberclass.ru/"
GET_USER_URL = "https://beta.sberclass.ru/services/graphql?mfe=dashboard&operation=GetCurrentUser"
GET_LESSONS_URL = "https://beta.sberclass.ru/services/graphql?mfe=mfe_electronic_diary_1_0_11&operation=getEDiaryData"

class Session:
    def __init__(self):
        self.username = ""
        self.password = ""
        self.logged_in = False
        self.session = requests.session()


    def login(self, username: str, password: str) -> bool:
        try:
            login_page = self.session.get(LOGIN_PAGE_URL) # необходимо для получения cookie и страницы для отправки post запроса
            login_url = login_page.text.split('data-loginAction="')[1].split('"')[0].replace("&amp;", "&") # небольшой быдлокод
            data = {
                "username": username,
                "password": password
            }
            login_req = self.session.post(login_url, data=data)
            if "Не удалось войти" in login_req.text:
                self.logged_in = False
            else:
                self.logged_in = True
        except: self.logged_in = False

        return self.logged_in
    

    def getLessons(self, day: str) -> list:
        """
        Дата должна быть в формате ГГГГ-ММ-ДД
        """
        json = {
            "operationName": "GetCurrentUser",
            "query": "query GetCurrentUser {\n  user {\n    getCurrentUser {\n      id\n      avatarUrl\n      firstName\n      middleName\n      lastName\n      status\n      studentRoles {\n        id\n        schoolId\n        status\n        school {\n          id\n          region {\n            regionId\n            __typename\n          }\n          __typename\n        }\n        stageGroup {\n          id\n          name\n          stage\n          __typename\n        }\n        __typename\n      }\n      teacherRoles {\n        id\n        status\n        school {\n          id\n          region {\n            regionId\n            __typename\n          }\n          __typename\n        }\n        subjects {\n          id\n          __typename\n        }\n        subjectGroups {\n          stage {\n            id\n            __typename\n          }\n          academicYear {\n            id\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      parentRoles {\n        id\n        status\n        school {\n          id\n          region {\n            regionId\n            __typename\n          }\n          __typename\n        }\n        childUserInfo {\n          id\n          studentRoles {\n            id\n            status\n            stageGroup {\n              id\n              name\n              stage\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
            "variables": {}
        }
        get_user_req = self.session.post(GET_USER_URL, json=json)
        headers = {
            "X-EDU-SCHOOL-ID": get_user_req.json()["data"]["user"]["getCurrentUser"]["studentRoles"][0]["schoolId"]
        }
        json = {
            "operationName": "getEDiaryData",
            "query": "query getEDiaryData($eDiaryRequestInput: EDiaryRequestInput!) {\n  eDiary {\n    getEDiaryData(eDiaryRequestInput: $eDiaryRequestInput) {\n      data {\n        lessonsByDate {\n          date\n          isHoliday\n          lessons {\n            lessonId\n            subjectName\n            lessonStartTime\n            lessonEndTime\n            marks {\n              markCustomName\n              weight\n              formControlName\n              temporaryMarkDate\n              comment {\n                comment\n                isStageSubjectGroupTeacher\n                user {\n                  id\n                  avatarUrl\n                  firstName\n                  middleName\n                  lastName\n                  __typename\n                }\n                __typename\n              }\n              isControlWork\n              createdUser {\n                id\n                avatarUrl\n                firstName\n                middleName\n                lastName\n                __typename\n              }\n              isStageSubjectGroupTeacher\n              __typename\n            }\n            classRoomName\n            linkOnlineLesson\n            isControlWork\n            lessonComment {\n              comment\n              isStageSubjectGroupTeacher\n              user {\n                id\n                avatarUrl\n                firstName\n                middleName\n                lastName\n                __typename\n              }\n              __typename\n            }\n            studentComment {\n              comment\n              isStageSubjectGroupTeacher\n              user {\n                id\n                avatarUrl\n                firstName\n                middleName\n                lastName\n                __typename\n              }\n              __typename\n            }\n            studentVisitStatus\n            lateTime\n            homeworkNotesNumber\n            homeworkTaskAndMaterialNumber\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      isSuccess\n      error {\n        errorCode\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
            "variables": {
                "eDiaryRequestInput": {
                    "dateFrom": day,
                    "period": "DAY"
                }
            }
        }
        get_lessons_req = self.session.post(GET_LESSONS_URL, headers=headers, json=json)
        try:
            return get_lessons_req.json()["data"]["eDiary"]["getEDiaryData"]["data"]["lessonsByDate"][0]["lessons"]
        except: return None