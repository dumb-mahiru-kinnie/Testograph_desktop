import flet as ft
from gistyc import GISTyc
from requests import get
from json import loads, dump
from functools import partial
from random import shuffle
from base64 import b64encode

class TestAPI:
    def __init__(self) -> None:
        self.answers_num = 0
        self.api = GISTyc(auth_token='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')
    def get_tests(self) -> dict:
        glist = self.api.get_gists()
        url = glist[0]['files']['tests.json']['raw_url']
        return loads(get(url).text)
    def send_test(self, test: dict) -> None:
        test['stars'] = '5'
        with open('test.json', 'w+', encoding='utf-8') as dumper:
            dumper.truncate(0)
            dump(test, dumper)
            #response = self.api.update_gist('tests.json')
Testograph = TestAPI()

def main(page: ft.Page):
    def test_entry(e: ft.ControlEvent, current_test: dict):
        clean_page()
        page.add(ft.Text(current_test['name']))
        page.add(ft.Image(current_test['image']))
        page.add(ft.Text(current_test['description']))
        page.add(ft.Text(f'Звёздный рейтинг: {current_test['stars']}'))
        page.add(ft.ElevatedButton('Назад', on_click=partial(update_tests)))
        page.add(ft.ElevatedButton('Вперёд', on_click=partial(progress, current_test=current_test, chosen_answers=[None] * len(current_test['questions']))))
    def progress(e: ft.ControlEvent, current_test: dict, chosen_answers: list, num_current_q:int=0):
        clean_page()
        current_q = current_test['questions'][num_current_q]
        page.add(ft.Text(current_q['question']))
        page.add(ft.Image(current_q['image']))
        match current_q['type']:
            case 'RADIO'|'CHECK':
                answers = current_q['answers']['right_answers'] + current_q['answers']['wrong_answers']
                shuffle(answers)
                match current_q['type']:
                    case 'RADIO':
                        def select_answer(e: ft.ControlEvent):
                            chosen_answers[num_current_q] = radios.value
                        radios = ft.RadioGroup(content=ft.Column(controls=[]), on_change=partial(select_answer))
                        if chosen_answers[num_current_q] != None:
                            radios.value = chosen_answers[num_current_q]
                        for each_answer in answers:
                            radios.content.controls.append(ft.Radio(value=each_answer, label=each_answer))
                        page.add(radios)
                    case 'CHECK':
                        answer = []
                        def select_answer(e: ft.ControlEvent):
                            if e.control.value:
                                answer.append(e.control.label)
                            else:
                                answer.remove(e.control.label)
                            chosen_answers[num_current_q] = answer
                        for each_answer in answers:
                            if chosen_answers[num_current_q] != None:
                                if each_answer in chosen_answers[num_current_q]:
                                    page.add(ft.Checkbox(label=each_answer, value=True, on_change=partial(select_answer)))
                                else:
                                    page.add(ft.Checkbox(label=each_answer, on_change=partial(select_answer)))
                            else:
                                page.add(ft.Checkbox(label=each_answer, on_change=partial(select_answer)))
            case 'ENTRY':
                def select_answer(e: ft.ControlEvent):
                    chosen_answers[num_current_q] = e.control.value
                if chosen_answers[num_current_q] != None:
                    page.add(ft.TextField(value=chosen_answers[num_current_q], multiline=True, min_lines=1, max_lines=10, on_change=partial(select_answer)))
                else:
                    page.add(ft.TextField(multiline=True, min_lines=1, max_lines=10, on_change=partial(select_answer)))
            case _:
                raise ValueError('Unrecognized question type')
        if num_current_q != len(current_test['questions']) - 1:
            page.add(ft.ElevatedButton('Вперёд', on_click=partial(progress, current_test=current_test, chosen_answers=chosen_answers, num_current_q=num_current_q + 1)))
        else:
            page.add(ft.ElevatedButton('Отправить результаты', on_click=partial(show_results, my_answers=chosen_answers, questions=current_test['questions'])))
        if num_current_q != 0:
            page.add(ft.ElevatedButton('Назад', on_click=partial(progress, current_test=current_test, chosen_answers=chosen_answers, num_current_q=num_current_q - 1)))
    def show_results(e: ft.ControlEvent, my_answers: list, questions: list):
        rights = 0
        wrongs = 0
        skips = 0
        all_q = len(questions)
        wrongs_list = []
        clean_page()
        for pos_q, question in enumerate(questions):
            match question['type']:
                case 'RADIO':
                    if my_answers[pos_q] in question['answers']['right_answers']:
                        rights += 1
                    elif my_answers[pos_q] == None:
                        skips += 1
                        wrongs_list.append([question['question'], 'Нет ответа', question['answers']['right_answers']])
                    else:
                        wrongs += 1
                        wrongs_list.append([question['question'], my_answers[pos_q], question['answers']['right_answers']])
                case 'CHECK':
                    if my_answers[pos_q] == None or my_answers[pos_q] == []:
                        skips += 1
                        wrongs_list.append([question['question'], 'Нет ответа', question['answers']['right_answers']])
                    elif set(my_answers[pos_q]) == set(question['answers']['right_answers']):
                        rights += 1
                    else:
                        wrongs += 1
                        wrongs_list.append([question['question'], my_answers[pos_q], question['answers']['right_answers']])
                case 'ENTRY':
                    if my_answers[pos_q] == None:
                        skips += 1
                        wrongs_list.append([question['question'], 'Нет ответа', question['answers']['right_answers']])
                    elif my_answers[pos_q].lower().strip() in question['answers']['right_answers']:
                        rights += 1
                    else:
                        wrongs += 1
                        wrongs_list.append([question['question'], my_answers[pos_q], question['answers']['right_answers']])
        chart = ft.PieChart(sections=[
            ft.PieChartSection((rights * 100) / all_q, color=ft.colors.GREEN, radius=100),
            ft.PieChartSection((wrongs * 100) / all_q, color=ft.colors.RED, radius=100),
            ft.PieChartSection((skips * 100) / all_q, color=ft.colors.GREY, radius=100)
        ])
        page.add(chart)
        page.add(ft.Text(f'Вы ответили правильно на {rights} вопросов из {all_q}'))
        if wrongs_list != []:
            page.add(ft.Text('Вот где были сделаны ошибки:'))
            table = ft.DataTable(columns=[
                ft.DataColumn(ft.Text('Вопрос')),
                ft.DataColumn(ft.Text('Ваш ответ')),
                ft.DataColumn(ft.Text('Правильные ответы'))
            ], rows=[])
            for wrong in wrongs_list:
                question_text, your_answer, correct_answers = wrong
                row = ft.DataRow(cells=[
                    ft.DataCell(ft.Text(question_text)),
                    ft.DataCell(ft.Text(str(your_answer))),
                    ft.DataCell(ft.Text(str(correct_answers)))
                ])
                table.rows.append(row)
            page.add(table)
        page.add(ft.ElevatedButton('Назад', on_click=partial(update_tests)))
    def update_tests(*e):
        clean_page()
        page.horizontal_alignment = 'CENTER'
        page.appbar.actions.extend([
            ft.IconButton(ft.icons.CREATE, on_click=partial(create_test)),
            ft.IconButton(ft.icons.REFRESH, on_click=partial(update_tests))
        ])
        tabs = ft.Tabs(tabs=[ft.Tab(text='Тесты'), ft.Tab(text='Видео')])
        page.add(tabs)
        tests = Testograph.get_tests()
        btn_list = []
        for test in tests:
            btn_list.append(ft.Image(src=test['image']))
            btn_list.append(ft.ElevatedButton(test['name'], on_click=partial(test_entry, current_test=test)))
        tabs.tabs[0].content = ft.GridView(controls=btn_list, expand=1, runs_count=5, max_extent=150, child_aspect_ratio=1.0, spacing=5, run_spacing=5)
        page.update()
    def clean_page():
        page.clean()
        page.appbar = ft.AppBar(
            leading=ft.Icon(ft.icons.BOOK), actions=[],
            title=ft.Text('Тестограф', theme_style=ft.TextThemeStyle.TITLE_LARGE)
        )
    def create_test(e: ft.ControlEvent):
        test = {'name': '', 'image': '', 'local': '', 'questions': []}
        def set_test_property(e: ft.ControlEvent, property: str):
            test[property] = e.control.value
        def pick_image(e: ft.FilePickerResultEvent):
            if e.files:
                selected_file.value = e.files[0].name
                selected_image.src = e.files[0].path
                test['local'] = e.files[0].path
                image_source.value = ''
                image_source.disabled = True
                with open(e.files[0].path, 'rb') as img:
                    test['image'] = str(b64encode(img.read()))
                page.update()
            else:
                image_source.disabled = False
                selected_file.value = ''
                selected_image.src = 'https://sklad-vlk.ru/d/cml_419459db_460fe794_2.jpg'
                test['image'] = ''
                page.update()
        image_picker = ft.FilePicker(on_result=pick_image)
        page.overlay.append(image_picker)
        clean_page()
        selected_file = ft.Text('')
        selected_image = ft.Image(src='https://sklad-vlk.ru/d/cml_419459db_460fe794_2.jpg', width=200, height=200)
        image_source = ft.TextField(label='Ссылка на картинку теста', on_change=partial(set_test_property, property='image'))
        page.add(ft.Column([
            ft.TextField(label='Название теста', on_change=partial(set_test_property, property='name')),
            image_source,
            ft.Text('или'),
            ft.ElevatedButton('Выбрать файл', icon=ft.icons.UPLOAD_FILE, on_click=lambda _: image_picker.pick_files(
                allow_multiple=False,
                dialog_title='Выберите картинку для теста',
                file_type=ft.FilePickerFileType.IMAGE
            ))
        ]))
        page.add(ft.Column([
            selected_file,
            selected_image,
            ft.TextField(label='Описание теста', multiline=True, min_lines=1, max_lines=10, on_change=partial(set_test_property, property='description')),
            ft.ElevatedButton('Перейти к вопросам', on_click=partial(create_question, test=test, pos=0))
        ]))
    def create_question(e: ft.ControlEvent, test: dict, pos: int):
        if test['name'].strip() == '':
            page.snack_bar = ft.SnackBar(ft.Text('Для создания теста необходимо название.'), duration=1000, open=True)
            page.update()
        else:
            clean_page()
            if len(test['questions']) == pos:
                test['questions'].append({
                    'question': '',
                    'type': '',
                    'image': '',
                    'local': '',
                    'answers': {
                        'right_answers': [],
                        'wrong_answers': []
                    }
                })
            def set_property_q(e: ft.ControlEvent, property: str):
                test['questions'][pos][property] = e.control.value
            def set_type_q(e: ft.ControlEvent):
                if test['questions'][pos]['type'] != e.control.value:
                    test['questions'][pos]['type'] = e.control.value
                    for control in page.controls:
                        if type(control) in [ft.RadioGroup, ft.Checkbox, ft.TextField] and control.label not in [f'Вопрос {pos + 1}', 'Ссылка на картинку']:
                            page.controls.remove(control)
                    match test['questions'][pos]['type']:
                        case 'RADIO':
                            page.add(ft.RadioGroup(ft.Column([])))
                        case 'CHECK'|'ENTRY':
                            page.add(ft.Column(controls=[]))
                    Testograph.answers_num = 0
                    page.update()
            selected_files = ft.Text('')
            selected_images = ft.Row([])
            selected_img_picker = ft.TextField(label='Ссылка на картинку', on_change=partial(set_property_q, property='image'))
            def pick_image(e: ft.FilePickerResultEvent):
                if e.files:
                    selected_files.value = ', '.join(map(lambda f: f.name, e.files))
                    for each_file in e.files:
                        selected_images.controls.append(ft.Image(each_file.path, width=100, height=100))
                        test['questions'][pos]['local'] += each_file.path
                        with open(each_file.path, 'rb') as img:
                            test['questions'][pos]['image'] += str(b64encode(img.read()))
                    selected_img_picker.value = ''
                    selected_img_picker.disabled = True
                    page.update()
                else:
                    selected_img_picker.disabled = False
                    selected_files.value = ''
                    selected_images.controls = []
                    test['questions'][pos]['image'] = ''
                    page.update()
            image_picker = ft.FilePicker(on_result=pick_image)
            page.overlay.append(image_picker)
            page.add(ft.Column([
                ft.TextField(label=f'Вопрос {pos + 1}', value=test['questions'][pos]['question'], on_change=partial(set_property_q, property='question')),
                selected_img_picker,
                ft.Text('или'),
                ft.ElevatedButton('Выбрать файл', icon=ft.icons.UPLOAD_FILE, on_click=lambda _: image_picker.pick_files(
                    allow_multiple=True,
                    dialog_title='Выберите картинки для теста',
                    file_type=ft.FilePickerFileType.IMAGE
                )),
                selected_files,
                selected_images,
                ft.Dropdown(options=[
                    ft.dropdown.Option('RADIO'),
                    ft.dropdown.Option('CHECK'),
                    ft.dropdown.Option('ENTRY')
                ], label='Тип вопроса', on_change=set_type_q)
            ]))
            def add_option(e: ft.ControlEvent):
                match test['questions'][pos]['type']:
                    case 'RADIO':
                        Testograph.answers_num += 1
                        radios = [x for x in page.controls if type(x) == ft.RadioGroup][0]
                        radios.content.controls.extend([
                            ft.Radio(value=str(Testograph.answers_num), label=f'{Testograph.answers_num}.'),
                            ft.TextField()
                        ])
                        def radio_clicked(e: ft.ControlEvent):
                            test['questions'][pos]['answers']['wrong_answers'] = []
                            for pos_control, control in enumerate(radios.content.controls):
                                if type(control) == ft.Radio:
                                    if control.value == radios.value:
                                        test['questions'][pos]['answers']['right_answers'] = [(radios.content.controls[pos_control + 1]).value]
                                    else:
                                        test['questions'][pos]['answers']['wrong_answers'] += [(radios.content.controls[pos_control + 1]).value]
                        radios.on_change = radio_clicked
                    case 'CHECK':
                        Testograph.answers_num += 1
                        column = [x for x in page.controls if type(x) == ft.Column][-1]
                        def check_clicked(e: ft.ControlEvent):
                            val = column.controls[column.controls.index(e.control) + 1].value
                            if e.control.value:
                                add = test['questions'][pos]['answers']['right_answers']
                                remove = test['questions'][pos]['answers']['wrong_answers']
                            else:
                                remove = test['questions'][pos]['answers']['right_answers']
                                add = test['questions'][pos]['answers']['wrong_answers']
                            if val not in add:
                                add += val
                            if val in remove:
                                remove.remove(val)
                        column.controls.extend([
                            ft.Checkbox(on_change=partial(check_clicked)),
                            ft.TextField()
                        ])
                    case 'ENTRY':
                        Testograph.answers_num += 1
                        column = [x for x in page.controls if type(x) == ft.Column][-1]
                        def entry_changed(e: ft.ControlEvent):
                            if len(test['questions'][pos]['answers']['right_answers']) == column.controls.index(e.control):
                                test['questions'][pos]['answers']['right_answers'].append(e.control.value)
                            else:
                                print(test['questions'][pos]['answers']['right_answers'])
                                test['questions'][pos]['answers']['right_answers'][column.controls.index(e.control)] = e.control.value
                        column.controls.append(ft.TextField(on_change=entry_changed))
                    case _:
                        page.snack_bar = ft.SnackBar(ft.Text('Сначала выбери тип вопроса!'), duration=1000, open=True)
                page.update()
            def delete_q(e: ft.ControlEvent):
                test['questions'].pop(pos)
                create_question(ft.ControlEvent, test, pos - 1)
            page.add(ft.FloatingActionButton(icon=ft.icons.ADD, on_click=add_option))
            if pos != 0:
                page.add(ft.IconButton(icon=ft.icons.DELETE, on_click=delete_q))
                page.appbar.actions.append(ft.IconButton(ft.icons.NAVIGATE_BEFORE, on_click=partial(create_question, test=test, pos=pos-1)))
            page.appbar.actions.extend([
                ft.IconButton(ft.icons.NAVIGATE_NEXT, on_click=partial(create_question, test=test, pos=pos+1)),
                ft.IconButton(ft.icons.DONE, on_click=partial(_send_test, test=test))
            ])
            page.update()
    def _send_test(e: ft.ControlEvent, test: dict):
        Testograph.send_test(test)
        update_tests()
    update_tests()

ft.app(target=main, name="testograph")