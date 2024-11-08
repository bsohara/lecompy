import PySimpleGUI as psg

# Apply a theme
psg.theme('DarkBlue13')

# Define table headings and initial data
headings = ['Código LECOM', 'OLT', 'ONT ou ONU', 'Roteador', 'FSAN/Nº série', 'Início', 'Fim', 'Responsável', 'Status', 'Observações']
data = [
    ['392.333', 'ZTE C350', 'Arcadyan PRV33AC1B', '-', 'JD20004ACE', '30/10/2024', '31/10/2024', 'Rhyan', 'Montado', 'Testes LPNet - Operações'],
    ['123.456', 'ZTE 650', 'Zyxel PMG2005', 'ZTE ZXHN H199A', 'ZTEGDFFE453C1', '30/04/2024', '01/05/2024', 'Bruno', 'Solicitado', '-']
]

# Left-sided menu layout
menu_layout = [
    [psg.Button('Dashboard', key='Dashboard', size=(20, 1), font=('Helvetica', 12))],
    [psg.Button('Visualizar', key='Visualizar', size=(20, 1), font=('Helvetica', 12))],
    [psg.Button('Registrar monitoramento', key='Registrar', size=(20, 1), font=('Helvetica', 12))],
    [psg.Button('Sair', size=(20, 1), font=('Helvetica', 12), button_color=('white', '#d9534f'))]
]

# Define each section layout
dashboard_layout = [
    [psg.Text('LECOMPY - Dashboard', font=('Helvetica', 18))],
    [psg.Table(values=data, headings=headings, key='table_alias', justification='center', auto_size_columns=False,
               display_row_numbers=False, col_widths=[12, 12, 15, 12, 15, 10, 10, 15, 12, 30], row_height=30,
               font=('Helvetica', 12), text_color='white', background_color='#1e1e2e', alternating_row_color='#2b2b3c',
               header_text_color='white', header_background_color='#3a3a5b', selected_row_colors=('white', '#007bff'))]
]

# Form layout for editing a selected record
edit_form_layout = [
    [psg.Text(f'{headings[i]}:', size=(15, 1)), psg.InputText('', key=f'field_{i}', size=(30, 1), disabled=(headings[i] != 'Status'))]
    for i in range(len(headings))
]
edit_form_layout.append([psg.Button('Atualizar', button_color=('white', '#5bc0de')), psg.Button('Cancelar', button_color=('white', '#d9534f'))])

# Layout for the registration form
registration_layout = [
    [psg.Text('Registrar Monitoramento', font=('Helvetica', 18))],
    [psg.Text('Código LECOM', size=(15, 1)), psg.InputText(key='codigo_lecom', size=(30, 1))],
    [psg.Text('OLT', size=(15, 1)), psg.Combo(['ZTE C350', 'ZTE C650', 'Zhone 219', 'Zhone 319', 'FiberHome 5', 'FiberHome 6', 'Huawei MA5800', 'Huawei MA5600', 'Nokia'], key='olt', size=(30, 1))],
    [psg.Text('ONT ou ONU', size=(15, 1)), psg.InputText(key='ont_ou_onu', size=(30, 1))],
    [psg.Text('Roteador', size=(15, 1)), psg.InputText(key='roteador', size=(30, 1), tooltip="Caso esteja provisionando com uma ONU Bridge, informar o modelo do roteador selecionado.")],
    [psg.Text('FSAN/Nº série', size=(15, 1)), psg.InputText(key='fsan_serial', size=(30, 1))],
    [psg.Text('Início', size=(15, 1)), psg.InputText(key='inicio', size=(30, 1))],
    [psg.Text('Fim', size=(15, 1)), psg.InputText(key='fim', size=(30, 1))],
    [psg.Text('Responsável', size=(15, 1)), psg.Combo(['Bruno', 'Eslier', 'Elenir', 'Guilherme', 'Jean', 'Renato', 'Rhyan'], key='responsavel', size=(30, 1))],
    [psg.Text('Status', size=(15, 1)), psg.Combo(['Solicitado', 'Montado', 'Desmontado e finalizado'], key='status', size=(28, 1))],
    [psg.Text('Observações', size=(15, 1)), psg.Multiline(size=(30, 3), key='observacoes')],
    [psg.Button('Registrar', button_color=('white', '#5bc0de')), psg.Button('Cancelar', button_color=('white', '#d9534f'))]
]

# Main window layout with menu on the left
layout = [
    [psg.Column(menu_layout, vertical_alignment='top'), psg.VerticalSeparator(),
     psg.Column(dashboard_layout, key='Dashboard_Section', visible=True),
     psg.Column(edit_form_layout, key='Edit_Section', visible=False),
     psg.Column(registration_layout, key='Register_Section', visible=False)]
]

# Create the main window
window = psg.Window('LECOMPY - Dashboard', layout, resizable=True, finalize=True)

# Event loop for the main window
current_section = 'Dashboard'
while True:
    event, values = window.read()

    if event in (psg.WINDOW_CLOSED, 'Sair'):
        break

    if event == 'Dashboard':
        # Switch to the Dashboard section
        window['Dashboard_Section'].update(visible=True)
        window['Edit_Section'].update(visible=False)
        window['Register_Section'].update(visible=False)
        current_section = 'Dashboard'

    elif event == 'Visualizar':
        # Check if a row is selected in the Dashboard table
        selected_row_idx = values.get('table_alias', None)
        
        if selected_row_idx and len(selected_row_idx) > 0:
            # Fill in the form with selected row data for editing
            row_idx = selected_row_idx[0]
            selected_row_data = data[row_idx]
            for i in range(len(headings)):
                window[f'field_{i}'].update(selected_row_data[i])

            # Switch to Edit section
            window['Dashboard_Section'].update(visible=False)
            window['Edit_Section'].update(visible=True)
            window['Register_Section'].update(visible=False)
            current_section = 'Edit'
        else:
            psg.popup('Selecione uma linha primeiro!', font=('Helvetica', 12), title='Aviso', background_color='#1e1e2e', text_color='white')

    elif event == 'Registrar':
        # Switch to the Registration section
        window['Dashboard_Section'].update(visible=False)
        window['Edit_Section'].update(visible=False)
        window['Register_Section'].update(visible=True)
        current_section = 'Registrar'

    elif current_section == 'Atualizar' and event == 'Save':
        # Update the data list with new "Status" value from Edit section
        data[row_idx][8] = values['field_8']  # Update only the Status field

        # Update the table with the modified data in the Dashboard section
        window['table_alias'].update(values=data)

        psg.popup('Registro atualizado com sucesso!', font=('Helvetica', 12), title='Sucesso', background_color='#1e1e2e', text_color='white')

        # Return to Dashboard section after saving
        window['Dashboard_Section'].update(visible=True)
        window['Edit_Section'].update(visible=False)
        window['Register_Section'].update(visible=False)
        current_section = 'Dashboard'

    elif current_section == 'Registrar' and event == 'Submit':
        # Handle registration logic here and add a new row to data if needed
        new_entry = [
            values['codigo_lecom'], values['olt'], values['ont_ou_onu'], values['roteador'],
            values['fsan_serial'], values['inicio'], values['fim'], values['responsavel'],
            values['status'], values['observacoes']
        ]
        data.append(new_entry)
        window['table_alias'].update(values=data)

        psg.popup('Registro adicionado com sucesso!', font=('Helvetica', 12), title='Sucesso', background_color='#1e1e2e', text_color='white')

        # Return to Dashboard section after submitting
        window['Dashboard_Section'].update(visible=True)
        window['Edit_Section'].update(visible=False)
        window['Register_Section'].update(visible=False)
        current_section = 'Dashboard'

window.close()
