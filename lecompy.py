import PySimpleGUI as psg
from datetime import datetime

# Define the menu layout
menu_layout = [
    [psg.Button('🏠 Dashboard', key='Dashboard', size=(20, 1), font=('Helvetica', 12))],
    [psg.Button('👁️ Visualizar', key='Visualizar', size=(20, 1), font=('Helvetica', 12))],
    [psg.Button('➕ Registrar monitoramento', key='Registrar', size=(20, 1), font=('Helvetica', 12))],
    [psg.Button('🚪 Sair', size=(20, 1), font=('Helvetica', 12), button_color=('white', '#d9534f'))]
]

# Define table headings and initial data
headings = ['Código LECOM','OLT', 'ONT ou ONU', 'Roteador', 'FSAN/Nº série ONT ou ONU', 'Nº série Roteador', 'Início', 'Fim', 'Responsável', 'Status', 'Observações']
data = [['123.456', 'ZTE C650', 'Blu-Castle BCKSV630', '-', 'BCKS76AB49FF', '-', '31/10/2024', '01/01/2024', 'Bruno', 'Solicitado', 'Testes de homologação ONT Blu-Castle para homologação']]

# Define the dashboard layout
dashboard_layout = [
    [psg.Text('LECOMPY - Dashboard', font=('Helvetica', 12))],
    [psg.Table(values=data, headings=headings, key='table_alias', justification='center', auto_size_columns=False,
               display_row_numbers=False, col_widths=[15] * len(headings), row_height=30,
               font=('Helvetica', 12), text_color='white', background_color='#1e1e2e', alternating_row_color='#2b2b3c',
               header_text_color='white', header_background_color='#3a3a5b', selected_row_colors=('white', '#007bff'), vertical_scroll_only=False)]
]

# Define the edit form layout
edit_form_layout = [
    [psg.Text(f'{headings[i]}:', size=(15, 1)), psg.InputText('', key=f'field_{i}', size=(30, 1), disabled=(headings[i] != 'Status'))]
    for i in range(len(headings))
]
edit_form_layout.append([psg.Button('Atualizar', button_color=('white', '#5bc0de')), psg.Button('Cancelar', key='Cancelar_Atualizacao', button_color=('white', '#d9534f'))])

# Define the registration form layout
registration_layout = [
    [psg.Text('Registrar Monitoramento', font=('Helvetica', 18))],
    [psg.Text('Código LECOM', size=(15, 1)), psg.InputText(key='codigo_lecom', size=(30, 1))],
    [psg.Text('OLT', size=(15, 1)), psg.Combo(['ZTE C350', 'ZTE C650', 'Zhone 219', 'Zhone 319', 'FiberHome 5', 'FiberHome 6', 'Huawei MA5800', 'Huawei MA5600', 'Nokia'], key='olt', size=(30, 1))],
    [psg.Text('ONT ou ONU', size=(15, 1)), psg.InputText(key='ont_ou_onu', size=(30, 1))],
    [psg.Text('Roteador', size=(15, 1)), psg.InputText(key='roteador', size=(30, 1), tooltip="Caso esteja provisionando com uma ONU Bridge, informar o modelo do roteador selecionado.")],
    [psg.Text('FSAN/Nº série ONT/ONU', size=(15, 1)), psg.InputText(key='fsan_serial_ont_onu', size=(30, 1))],
    [psg.Text('Nº série Roteador', size=(15, 1)), psg.InputText(key='serial_roteador', size=(30, 1))],
    [psg.Text('Início', size=(15, 1)), psg.InputText(key='inicio', size=(30, 1))],
    [psg.Text('Fim', size=(15, 1)), psg.InputText(key='fim', size=(30, 1))],
    [psg.Text('Responsável', size=(15, 1)), psg.Combo(['Bruno', 'Eslier', 'Elenir', 'Guilherme', 'Jean', 'Renato', 'Rhyan'], key='responsavel', size=(30, 1))],
    [psg.Text('Status', size=(15, 1)), psg.Combo(['Solicitado', 'Montado', 'Desmontado e finalizado'], key='status', size=(28, 1))],
    [psg.Text('Observações', size=(15, 1)), psg.Multiline(size=(30, 3), key='observacoes')],
    [psg.Button('💾 Registrar', key='Confirmar_Registro', button_color=('white', '#5bc0de')), psg.Button('Cancelar', key='Cancelar_Registro', button_color=('white', '#d9534f'))]
]

# Main window layout with menu on the left
layout = [
    [psg.Column(menu_layout, vertical_alignment='top'), psg.VerticalSeparator(),
     psg.Column(dashboard_layout, key='Dashboard_Section', visible=True),
     psg.Column(edit_form_layout, key='Edit_Section', visible=False),
     psg.Column(registration_layout, key='Register_Section', visible=False)]
]

# Create the main window
window = psg.Window('LECOMPY - Dashboard', layout, size=(1000,450), resizable=True, finalize=True)

# Event loop for the main window
current_section = 'Dashboard'
row_idx = None  # Track row index in edit mode

while True:
    event, values = window.read()

    if event in (psg.WINDOW_CLOSED, 'Sair'):
        break

    if event == 'Dashboard':
        window['Dashboard_Section'].update(visible=True)
        window['Edit_Section'].update(visible=False)
        window['Register_Section'].update(visible=False)

    elif event == 'Visualizar':
        selected_row_idx = values.get('table_alias', None)
        if selected_row_idx and len(selected_row_idx) > 0:
            row_idx = selected_row_idx[0]
            selected_row_data = data[row_idx]
            for i in range(len(headings)):
                window[f'field_{i}'].update(selected_row_data[i])
            window['Dashboard_Section'].update(visible=False)
            window['Edit_Section'].update(visible=True)
            window['Register_Section'].update(visible=False)
        else:
            psg.popup('Selecione uma linha primeiro!', font=('Helvetica', 12), title='Aviso', background_color='#1e1e2e', text_color='white')

    elif event == 'Registrar':
        window['Dashboard_Section'].update(visible=False)
        window['Edit_Section'].update(visible=False)
        window['Register_Section'].update(visible=True)

    elif event == 'Atualizar' and row_idx is not None:
        updated_status = values['field_9']
        data[row_idx][9] = updated_status
        window['table_alias'].update(values=data)
        psg.popup('Registro atualizado com sucesso!', font=('Helvetica', 12), title='Sucesso', background_color='#1e1e2e', text_color='white')
        window['Dashboard_Section'].update(visible=True)
        window['Edit_Section'].update(visible=False)

    elif event == 'Confirmar_Registro':
        # Check all required fields
        if all(values[key] for key in ['codigo_lecom', 'olt', 'ont_ou_onu', 'status', 'responsavel', 'inicio', 'fim']):
            try:
                inicio = datetime.strptime(values['inicio'], "%d/%m/%Y")
                fim = datetime.strptime(values['fim'], "%d/%m/%Y")
            except ValueError:
                psg.popup('Formato de data inválido! Use DD/MM/YYYY.', font=('Helvetica', 12), title='Erro', background_color='#1e1e2e', text_color='white')
                continue
            
            new_entry = [
                values['codigo_lecom'], values['olt'], values['ont_ou_onu'], values['roteador'],
                values['fsan_serial_ont_onu'], values['serial_roteador'], values['inicio'], values['fim'], 
                values['responsavel'], values['status'], values['observacoes'].strip()
            ]
            data.append(new_entry)
            window['table_alias'].update(values=data)
            psg.popup('Registro adicionado com sucesso!', font=('Helvetica', 12), title='Sucesso', background_color='#1e1e2e', text_color='white')
            window['Dashboard_Section'].update(visible=True)
            window['Register_Section'].update(visible=False)
        else:
            psg.popup('Por favor, preencha todos os campos obrigatórios!', font=('Helvetica', 12), title='Erro', background_color='#1e1e2e', text_color='white')


    elif event == 'Cancelar_Registro':
        # Volta para a página do dashboard ao cancelar o registro
        window['Register_Section'].update(visible=False)
        window['Dashboard_Section'].update(visible=True)
        
    elif event == 'Cancelar_Atualizacao':
        # Volta para a página do dashboard ao cancelar o registro
        window['Register_Section'].update(visible=False)
        window['Dashboard_Section'].update(visible=True)
        window['Edit_Section'].update(visible=False)

window.close()
