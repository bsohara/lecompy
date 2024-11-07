import PySimpleGUI as psg

headings = ['Código LECOM', 
            'OLT',
            'ONT ou ONU',
            'Roteador',
            'FSAN/Nº série',
            'Início',
            'Fim',
            'Responsável',
            'Status',
            'Observações']

data = [
    ['392.333',
     'ZTE C350',
     'Arcadyan PRV33AC1B',
     '-',
     'JD20004ACE',
     '30/10/2024',
     '31/10/2024',
     'Rhyan',
     'Montado',
     'Testes LPNet - Operações'],
     ['123.456',
     'ZTE 650',
     'Zyxel PMG2005',
     'ZTE ZXHN H199A',
     'ZTEGDFFE453C1',
     '30/04/2024',
     '01/05/2024',
     'Bruno',
     'Solicitado',
     '-']
]

layout = [
    [psg.Table(values=data, headings=headings, key='table_alias', justification='right')],
    [psg.Button('Visualizar'), psg.Button('Registrar monitoramento')]
]

"""
form_layout = [

]
"""



window = psg.Window('LECOMPY', layout)

while True:
    event, values = window.read()

    if event == psg.WINDOW_CLOSED or event == 'Sair':
        break

    if event == 'Visualizar':
        # Check if a row is selected
        selected_row_idx = values.get('table_alias', None)
        
        if selected_row_idx and len(selected_row_idx) > 0:
            # Get the selected row index and retrieve corresponding data from the data list
            selected_row_data = data[selected_row_idx[0]]  # Since `selected_row_idx` is a list of indices
            
            # Prepare header and data pairs
            header_data = "\n".join([f"{head}: {selected_row_data[i]}" for i, head in enumerate(headings)])
            
            # Show the data in the popup
            psg.popup('Linha selecionada:', header_data)
        else:
            psg.popup('Nenhuma linha selecionada')

    if event == 'Registrar monitoramento':
        registration_form_window = psg.Window('LECOMPY - Registro de monitoramento')

window.close()