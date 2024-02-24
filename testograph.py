import flet as ft


def main(page: ft.Page):
    page.add(
        ft.Row(controls=[
            ft.Text('A'),
            ft.Text('B'),
            ft.Text('C'),
            ft.ElevatedButton('D!!')
        ])
    )



ft.app(target=main, name="testograph")