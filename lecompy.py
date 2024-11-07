import PySimpleGUI as psg

headings = ['Código LECOM', 
            'OLT',
            'ONT_ONU',
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
     'Testes LPNet - Operações']
]

layout = [
    [psg.Table(values=data, headings=headings, key='table_alias', justification='right')],
    [psg.Button('Visualizar'), psg.Button('Sair'), psg.Button('Registrar monitoramento')]
]

window = psg.Window('LECOMPY', layout)

while True:
    event, values = window.read()
    
    selected_row_idx = values['table_alias']
        
    if selected_row_idx:
        # Get the selected row index and retrieve corresponding data from the data list
        selected_row_data = data[selected_row_idx[0]]  # Since `selected_row_idx` is a list of indices
        psg.popup('Linha selecionada:', selected_row_data)
    else:
        psg.popup('Nenhuma linha selecionada')

window.close()