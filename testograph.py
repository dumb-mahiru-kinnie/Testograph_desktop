import flet as ft


def main(page: ft.Page):
    page.add(ft.Text('Тестограф', theme_style=ft.TextThemeStyle.TITLE_LARGE))
    tabs = ft.Tabs(
        tabs=[
            ft.Tab(
                text='Тесты',
                content=ft.Container(
                    content=ft.Text('Save me')
                )
            ),
            ft.Tab(
                text='Видео'
            )
        ]
    )
    page.add(tabs)



ft.app(target=main, name="testograph")