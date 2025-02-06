import flet as ft
import networking
from datetime import datetime, timedelta

day = datetime.today()
indexes = ["₀", "₁", "₂", "₃", "₄", "₅"]
session = networking.Session()

def login(username: str, password: str, page: ft.Page):
    session.login(username, password)
    if not session.logged_in:
        alert = ft.AlertDialog(
            title=ft.Text("Ошибка"),
            content=ft.Text("Ошибка входа в аккаунт. Проверьте логин, пароль а также интернет-соединение."),
            actions=[ft.TextButton("Закрыть", on_click=lambda x: page.close(alert))]
        )
        page.open(alert)
    else:
        dashboard(page)


def main(page: ft.Page):
    page.title = "СберКласс"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    main_text = ft.Text("СберКласс", size=24, weight=ft.FontWeight.BOLD)
    username_inp = ft.TextField(label="Логин", width=300)
    password_inp = ft.TextField(label="Пароль", password=True, width=300)
    login_button = ft.ElevatedButton(text="Вход", width=300, on_click=lambda x: login(username_inp.value, password_inp.value, page))

    page.add(main_text, username_inp, password_inp, login_button)


def generateMarks(marks) -> str:
    if not marks:
        return ""
    result = []
    for mark in marks:
        result.append(f"{mark["markCustomName"]}{indexes[int(mark["weight"])]}")
    return " ".join(result)


def generateControls(lesson):
    controls = [
        ft.Text(f"{lesson["subjectName"]} " + generateMarks(lesson["marks"]), size=24, weight=ft.FontWeight.BOLD),
        ft.Text(f"{lesson["lessonStartTime"]} - {lesson["lessonEndTime"]} | {lesson["classRoomName"]}", color=ft.Colors.ON_SECONDARY_CONTAINER)
    ]
    if lesson["homeworkTaskAndMaterialNumber"] or int(lesson["homeworkNotesNumber"]):
        controls.append(ft.Divider(
            height=5, color=ft.Colors.SECONDARY_CONTAINER
        ))
        controls.append(ft.ElevatedButton(
            text=f"📖 {int(lesson["homeworkTaskAndMaterialNumber"]) + int(lesson["homeworkNotesNumber"])}",
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(
                    size=16,
                    weight=ft.FontWeight.BOLD
                )
            )
        ))
    return controls

def dashboard(page: ft.Page):
    page.clean()
    page.vertical_alignment = ft.CrossAxisAlignment.START

    def update_all():
        date_button.text = day.strftime("%d.%m.%Y")
        update_lessons()
        page.update()

    def handle_change(e):
        global day
        day = e.control.value
        update_all()

    def update_day(next: bool):
        global day
        day = day + timedelta(days=1 if next else -1)
        main_col.controls.clear()
        update_all()

    main_col = ft.Column(
        spacing=10,
        height=page.height,
        width=page.width,
        scroll=ft.ScrollMode.HIDDEN
    )

    def update_lessons():
        global lessons
        lessons = session.getLessons(day.strftime("%Y-%m-%d"))
        main_col.controls.clear()
        for lesson in lessons:
            main_col.controls.append(
                ft.Container(
                    ink=True,
                    bgcolor=ft.Colors.SECONDARY_CONTAINER,
                    padding=20,
                    width=page.width,
                    border_radius=20,
                    content=ft.Column(
                        spacing=0,
                        controls=generateControls(lesson)
                    )
                )
            )

        if not lessons:
            main_col.controls.append(ft.Text("Сегодня уроков нет, отдыхаем :D", size=24, weight=ft.FontWeight.BOLD))

        main_col.controls.append( # это такой ужас, помогите пофиксить, кто-нибудь, пжпжпж
            ft.Container(
                bgcolor=ft.Colors.SURFACE,
                height=140
            )
        )

    date_button = ft.ElevatedButton(
        text=day.strftime("%d.%m.%Y"),
        icon = ft.Icons.CALENDAR_MONTH,
        on_click=lambda e: page.open(
            ft.DatePicker(
                current_date=day,
                on_change=handle_change
            )
        )
    )

    prev_day_button = ft.IconButton(
        icon=ft.icons.NAVIGATE_BEFORE_ROUNDED,
        on_click=lambda e: update_day(False)
    )

    next_day_button = ft.IconButton(
        icon=ft.icons.NAVIGATE_NEXT_ROUNDED,
        on_click=lambda e: update_day(True)
    )

    cont = ft.Container(
        content=ft.Row(
            controls=[
                prev_day_button,
                date_button,
                next_day_button
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
    )

    update_lessons()
    page.add(ft.Divider(color=ft.Colors.SURFACE), cont, ft.Divider(), main_col)

ft.app(main)