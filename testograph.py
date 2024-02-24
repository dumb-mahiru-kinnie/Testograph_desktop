import flet as ft


def main(page: ft.Page):
    page.horizontal_alignment = 'CENTER'
    page.add(ft.Text('Тестограф', theme_style=ft.TextThemeStyle.TITLE_LARGE))
    tabs = ft.Tabs(
        tabs=[
            ft.Tab(
                text='Тесты',
                content=ft.Container(
                    content=ft.Text('')
                )
            ),
            ft.Tab(
                text='Видео'
            )
        ]
    )
    page.add(tabs)



ft.app(target=main, name="testograph")