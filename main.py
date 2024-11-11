import PySimpleGUI as psg
import csv
import sqlite3 as sql3

# Funções de banco de dados
def connect_to_db(db_name="lecompy_data.db"):
    conn = sql3.connect(db_name)
    conn.execute("PRAGMA busy_timeout = 5000")
    cursor = conn.cursor()
    return conn, cursor

def fetch_all_data():
    conn, cursor = connect_to_db()
    cursor.execute('SELECT codigo_lecom, olt, ont_ou_onu, roteador, fsan_serial_ont_onu, serial_roteador, inicio, fim, responsavel, status, observacoes FROM registros')
    rows = cursor.fetchall()
    conn.close()
    return rows

def insert_data(codigo_lecom, olt, ont_ou_onu, roteador, fsan_serial_ont_onu, serial_roteador, inicio, fim, responsavel, status, observacoes):
    conn, cursor = connect_to_db()
    cursor.execute('''INSERT INTO registros 
                      (codigo_lecom, olt, ont_ou_onu, roteador, fsan_serial_ont_onu, serial_roteador, inicio, fim, responsavel, status, observacoes)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (codigo_lecom, olt, ont_ou_onu, roteador, fsan_serial_ont_onu, serial_roteador, inicio, fim, responsavel, status, observacoes))
    conn.commit()
    conn.close()

def update_data(id, *values):
    conn, cursor = connect_to_db()
    cursor.execute('''UPDATE registros SET codigo_lecom=?, olt=?, ont_ou_onu=?, roteador=?, fsan_serial_ont_onu=?, serial_roteador=?, 
                      inicio=?, fim=?, responsavel=?, status=?, observacoes=? WHERE id=?''', (*values, id))
    conn.commit()
    conn.close()

def delete_data(id):
    conn, cursor = connect_to_db()
    cursor.execute('DELETE FROM registros WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def create_table():
    conn, cursor = connect_to_db()
    cursor.execute('''CREATE TABLE IF NOT EXISTS registros (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        codigo_lecom TEXT,
                        olt TEXT,
                        ont_ou_onu TEXT,
                        roteador TEXT,
                        fsan_serial_ont_onu TEXT,
                        serial_roteador TEXT,
                        inicio TEXT,
                        fim TEXT,
                        responsavel TEXT,
                        status TEXT,
                        observacoes TEXT)''')
    conn.commit()
    conn.close()

create_table()

# Layouts
headings = ['Código LECOM', 'OLT', 'ONT ou ONU', 'Roteador', 'FSAN/Nº série ONT ou ONU', 'Nº série Roteador', 'Início', 'Fim', 'Responsável', 'Status', 'Observações']
menu_layout = [[psg.Button('🏠 Dashboard', key='Dashboard')], [psg.Button('👁 Visualizar', key='Visualizar')], 
               [psg.Button('➕ Registrar monitoramento', key='Registrar')], [psg.Button('🚪 Sair', key='Sair')]]

dashboard_layout = [[psg.Text('LECOMPY - Dashboard')],
                    [psg.Table(values=fetch_all_data(), headings=headings, key='table_alias', auto_size_columns=False,
                               display_row_numbers=False, col_widths=[15] * len(headings), row_height=30)],
                    [psg.Button('📄 Exportar CSV', key='Exportar_CSV')]]

edit_form_layout = [[psg.Text(f'{headings[i]}:'), psg.InputText('', key=f'field_{i}')] for i in range(len(headings))] + \
                   [[psg.Button('Atualizar'), psg.Button('Excluir', key='Excluir_Item')]]

registration_layout = [[psg.Text('Registrar Monitoramento')]] + \
                     [[psg.Text(headings[i]), psg.InputText(key=f'reg_field_{i}')] for i in range(len(headings))] + \
                     [[psg.Button('💾 Confirmar Registro'), psg.Button('Cancelar', key='Cancelar_Registro')]]

# Função principal
def main_window():
    layout = [[psg.Column(menu_layout, vertical_alignment='top'), psg.VerticalSeparator(),
               psg.Column(dashboard_layout, key='Dashboard_Section', visible=True),
               psg.Column(edit_form_layout, key='Edit_Section', visible=False),
               psg.Column(registration_layout, key='Register_Section', visible=False)]]

    window = psg.Window('LECOMPY - Dashboard', layout, resizable=True, finalize=True)
    data = fetch_all_data()
    row_idx = None

    while True:
        event, values = window.read()

        if event == psg.WINDOW_CLOSED or event == 'Sair':
            break

        if event == 'Dashboard':
            window['Dashboard_Section'].update(visible=True)
            window['Edit_Section'].update(visible=False)
            window['Register_Section'].update(visible=False)

        elif event == 'Registrar':
            window['Dashboard_Section'].update(visible=False)
            window['Edit_Section'].update(visible=False)
            window['Register_Section'].update(visible=True)

        elif event == 'Confirmar Registro':
            if all(values.get(f'reg_field_{i}') for i in range(len(headings))):
                insert_data(*[values[f'reg_field_{i}'] for i in range(len(headings))])
                data = fetch_all_data()
                window['table_alias'].update(values=data)
                psg.popup('Registro adicionado com sucesso!', title='Sucesso')
                window['Dashboard_Section'].update(visible=True)
                window['Register_Section'].update(visible=False)
            else:
                psg.popup('Preencha todos os campos!', title='Erro')

        elif event == 'Visualizar':
            selected_row_idx = values.get('table_alias', [])
            if selected_row_idx:
                row_idx = selected_row_idx[0]
                selected_row_data = data[row_idx][1:]
                for i, val in enumerate(selected_row_data):
                    window[f'field_{i}'].update(val)
                window['Dashboard_Section'].update(visible=False)
                window['Edit_Section'].update(visible=True)

        elif event == 'Atualizar' and row_idx is not None:
            updated_values = [values[f'field_{i}'] for i in range(len(headings))]
            update_data(data[row_idx][0], *updated_values)
            data = fetch_all_data()
            window['table_alias'].update(values=data)
            psg.popup('Registro atualizado com sucesso!', title='Sucesso')
            window['Dashboard_Section'].update(visible=True)
            window['Edit_Section'].update(visible=False)

        elif event == 'Excluir_Item' and row_idx is not None:
            delete_data(data[row_idx][0])
            data = fetch_all_data()
            window['table_alias'].update(values=data)
            psg.popup('Registro excluído com sucesso!', title='Sucesso')
            window['Dashboard_Section'].update(visible=True)
            window['Edit_Section'].update(visible=False)

        elif event == 'Exportar_CSV':
            file_path = psg.popup_get_file('Salvar como', save_as=True, default_extension='.csv', file_types=(("CSV Files", "*.csv"),))
            if file_path:
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(headings)
                    writer.writerows(data)
                psg.popup('Arquivo CSV salvo com sucesso!', title='Sucesso')

    window.close()

main_window()
