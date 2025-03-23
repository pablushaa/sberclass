import requests

LOGIN_PAGE_URL = "https://auth.sberclass.ru/auth/realms/EduPowerKeycloak/protocol/openid-connect/auth?response_type=code&client_id=edupower&scope=openid%20profile%20email&redirect_uri=https://newschool.sberclass.ru/services/auth/login/oauth2/code/edupower?returnTo%3Dhttps://newschool.sberclass.ru/"
GET_USER_URL = "https://beta.sberclass.ru/services/graphql?mfe=dashboard&operation=GetCurrentUser"
GET_LESSONS_URL = "https://beta.sberclass.ru/services/graphql?mfe=mfe_electronic_diary_1_0_11&operation=getEDiaryData"
GET_LESSON_URL = "https://beta.sberclass.ru/services/graphql?mfe=dashboard&operation=getStudentCurrentLesson"

class Session:
    def __init__(self):
        self.username = ""
        self.password = ""
        self.userid = ""
        self.schoolid = ""
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
        self.userid = get_user_req.json()["data"]["user"]["getCurrentUser"]["id"]
        self.schoolid = get_user_req.json()["data"]["user"]["getCurrentUser"]["studentRoles"][0]["schoolId"]
        headers = {
            "X-EDU-SCHOOL-ID": self.schoolid
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

    
    def getStudentLesson(self, lessonid: str) -> list:
        json = {"operationName":"getStudentCurrentLesson","variables":{"lessonId":lessonid,"userId":self.userid},"query":"query getStudentCurrentLesson($userId: UUID, $lessonId: ID!) {\n  student {\n    getStudentCurrentLessonCWorkHWorkByLessonId(\n      userId: $userId\n      lessonId: $lessonId\n    ) {\n      lessonsCompact {\n        id\n        lessonNumber\n        classRoomName\n        start\n        end\n        subject {\n          id\n          name\n          fullName\n          tenantShortName\n          __typename\n        }\n        plan {\n          lessonPlanId\n          authorUserId\n          authorName\n          updateTs\n          lessonId\n          lessonStart\n          lessonEnd\n          goalId\n          goalName\n          goalStartDate\n          goalEndDate\n          subjectId\n          subjectName\n          stageSubjectGroupId\n          stageSubjectGroupName\n          lessonTopic\n          homework\n          isVideoLesson\n          videoLessonLink\n          videoconferenceType\n          isPublished\n          isArchived\n          isShared\n          lessonPlanNotes {\n            ...lessonPlanNotesFragment\n            __typename\n          }\n          lessonPlanTasks {\n            ...lessonPlanTasksFragment\n            __typename\n          }\n          lessonPlanMaterials {\n            lessonPlanMaterialId\n            lessonId\n            order\n            catalogItemId\n            contentName\n            contentType\n            previewUrl\n            __typename\n          }\n          __typename\n        }\n        lessonWithoutPlanNotes {\n          ...lessonPlanNotesFragment\n          __typename\n        }\n        lessonWithoutPlanTasks {\n          ...lessonPlanTasksFragment\n          __typename\n        }\n        controlWork {\n          id\n          classSubjectControlWork {\n            id\n            name\n            __typename\n          }\n          module {\n            id\n            title\n            __typename\n          }\n          planTime\n          startTime\n          closeTime\n          duration\n          status\n          markTime\n          visible\n          studentInSubgroupId\n          variant {\n            id\n            tasks {\n              taskId\n              __typename\n            }\n            __typename\n          }\n          mark {\n            id\n            governmentMark\n            customName\n            isAccepted\n            abbreviation\n            iconName\n            __typename\n          }\n          __typename\n        }\n        previousLessonOnSubject {\n          id\n          date\n          __typename\n        }\n        nextLessonOnSubject {\n          id\n          date\n          __typename\n        }\n        teacher {\n          ...teacherFragment\n          __typename\n        }\n        studentModuleModel {\n          ...moduleModelFragment\n          __typename\n        }\n        studentPlanModuleCounter\n        __typename\n      }\n      homework {\n        homeworkId\n        deadlineTs\n        note\n        subject {\n          id\n          __typename\n        }\n        homeworkTasks {\n          task {\n            id\n            type\n            laboriousness\n            subjectName\n            title\n            checkTypes\n            __typename\n          }\n          studentTask {\n            taskMark {\n              id\n              governmentMark\n              __typename\n            }\n            status\n            taskMessages {\n              taskId\n              messageSource\n              readFacts {\n                messageId\n                createTime\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment lessonPlanNotesFragment on LessonPlanNote {\n  lessonPlanNoteId\n  lessonId\n  lessonStart\n  note\n  lessonPlanNoteType\n  isHomeWork\n  order\n  __typename\n}\n\nfragment lessonPlanTasksFragment on LessonPlanTask {\n  status\n  taskMark {\n    id\n    governmentMark\n    __typename\n  }\n  type\n  checkTypes\n  taskDeadline {\n    deadline\n    __typename\n  }\n  taskMessages {\n    taskId\n    messageSource\n    readFacts {\n      messageId\n      createTime\n      __typename\n    }\n    __typename\n  }\n  lessonPlanTaskId\n  lessonId\n  lessonStart\n  goalElementId\n  taskId\n  title\n  assignmentType\n  laboriousness\n  isHomeWork\n  order\n  __typename\n}\n\nfragment teacherFragment on Teacher {\n  id\n  user {\n    id\n    lastName\n    firstName\n    middleName\n    avatarUrl\n    externalSession\n    __typename\n  }\n  __typename\n}\n\nfragment moduleModelFragment on StudentModule {\n  id\n  isActive\n  moduleTitle\n  moduleShortDesc\n  subjectTitle\n  deadLineDate\n  startDate\n  subjectId\n  maxClosedByTeacherLevel\n  plannedLevel\n  studentTargetGoalLevel\n  isReflectionPassed\n  taskCount\n  completedTaskCount\n  achieveInfo {\n    isAchieved\n    maxAchievedLevel\n    __typename\n  }\n  personalControlWorks {\n    id\n    duration\n    __typename\n  }\n  __typename\n}\n"}
        headers = {
            "X-EDU-SCHOOL-ID": self.schoolid
        }
        get_lesson_req = self.session.post(GET_LESSON_URL, headers=headers, json=json)
        result = []
        try:
            result.extend(list(get_lesson_req.json()["data"]["student"]["getStudentCurrentLessonCWorkHWorkByLessonId"]["lessonsCompact"]["lessonWithoutPlanNotes"]))
        except: pass
        try:
            result.extend(list(get_lesson_req.json()["data"]["student"]["getStudentCurrentLessonCWorkHWorkByLessonId"]["lessonsCompact"]["plan"]["lessonPlanNotes"]))
        except: pass
        if not result or len(result) == 0:
            return ["Это ДЗ необходимо просмотреть на сайте СберКласса. На данный момент просмотр и, тем более, выполнение интерактивного ДЗ невозможно (или произошел какой-то сбой. Если это так, то просьба открыть issue на GitHub'e проекта)"]
        return result