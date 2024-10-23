from searchEnginePublications_copy.searchEnginePublications.main import *


def search_window():
    layout = [
        [sg.Text('Results:', font='Any 15')],
        [sg.Listbox(values=[], size=(80, 20), key='results')],
        [sg.Button('Open', disabled=True), sg.Button('Close')]
    ]
    window = sg.Window('Search Results', layout, size=(800, 600))
    return window

def update_search_window(window, results):
    window['results'].update(list(results.keys()))
    if len(results) > 0:
        window['Open'].update(disabled=False)
    else:
        window['Open'].update(disabled=True)

sg.theme('LightGrey1')

layout = [
    [sg.Text('Enter query:')],
    [sg.InputText(key='query')],
    [sg.Button('Search')],
    [sg.HorizontalSeparator()],
    [sg.Text('Results:')],
    [sg.Listbox(values=[], size=(80, 20), key='results')],
    [sg.HorizontalSeparator()],
    [sg.Button('Open', disabled=True), sg.Button('Exit')]
]

window = sg.Window('CSM Search Publications', layout)

search_window_active = False

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    if event == 'Search':
        query = values['query']
        search_query(query)
        window['results'].update(list(display_result.keys()))
        if not search_window_active:
            search_window_active = True
            search_window = search_window()

        update_search_window(search_window, display_result)

    if event == 'results':
        selected_item = values['results'][0]
        selected_item_dict = display_result[selected_item]
        webbrowser.open(selected_item_dict['title_link'], new=2)

    if len(values['results']) > 0:
        window['Open'].update(disabled=False)
    else:
        window['Open'].update(disabled=True)

    if search_window_active:
        search_event, search_values = search_window.read(timeout=0)
        if search_event == sg.WIN_CLOSED or search_event == 'Close':
            search_window.close()
            search_window_active = False

window.close()