import PySimpleGUI as psg
import csv
import sqlite3 as sql3

# Configuração do tema e estilo moderno
psg.theme('SystemDefaultForReal')  # Tema neutro

# Definindo cores e estilo do layout
button_style = {'button_color': ('#FFFFFF', '#007ACC'), 'size': (20, 2), 'border_width': 0, 'font': ('Segoe UI', 10)}
table_style = {'background_color': '#EAEAEA', 'text_color': '#333333', 'font': ('Segoe UI', 10)}
header_font = ('Segoe UI', 12, 'bold')

# Funções de banco de dados
def connect_to_db(db_name="lecompy_data.db"):
    conn = sql3.connect(db_name)
    conn.execute("PRAGMA busy_timeout = 5000")
    cursor = conn.cursor()
    return conn, cursor

# Funções de registros
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
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT)''')
    # Inserir um usuário padrão (admin/admin) para o primeiro acesso
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ('admin', 'admin'))
    conn.commit()
    conn.close()

create_table()

# Funções de autenticação
def verify_credentials(username, password):
    conn, cursor = connect_to_db()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Função de login
def login_window():
    layout = [
        [psg.Text('Usuário:', font=('Segoe UI', 12)), psg.InputText(key='username', font=('Segoe UI', 10))],
        [psg.Text('Senha:', font=('Segoe UI', 12)), psg.InputText(key='password', password_char='*', font=('Segoe UI', 10))],
        [psg.Button('Entrar', size=(10, 1)), psg.Button('Sair', size=(10, 1))]
    ]
    window = psg.Window('LECOMPY - Login', layout, finalize=True)
    
    while True:
        event, values = window.read()
        
        if event == psg.WINDOW_CLOSED or event == 'Sair':
            window.close()
            return None  # Retorna None se o usuário sair
        
        if event == 'Entrar':
            username = values['username']
            password = values['password']
            if verify_credentials(username, password):
                window.close()
                return username  # Retorna o nome do usuário logado
            else:
                psg.popup('Usuário ou senha incorretos. Tente novamente.', title='Erro')

# Layouts principais
headings = ['Código LECOM', 'OLT', 'ONT ou ONU', 'Roteador', 'FSAN/Nº série ONT ou ONU', 'Nº série Roteador', 'Início', 'Fim', 'Responsável', 'Status', 'Observações']
menu_layout = [[psg.Button('🏠 Dashboard', key='Dashboard', **button_style)], 
               [psg.Button('👁 Visualizar', key='Visualizar', **button_style)], 
               [psg.Button('➕ Registrar', key='Registrar', **button_style)], 
               [psg.Button('🚪 Sair', key='Sair', **button_style)]]

dashboard_layout = [
    [psg.Text('📊 LECOMPY - Dashboard', font=header_font, text_color='#007ACC')],
    [psg.Table(values=fetch_all_data(), headings=headings, key='table_alias', auto_size_columns=False,
               display_row_numbers=False, col_widths=[15] * len(headings), row_height=30, header_font=header_font,
               **table_style)],
    [psg.Button('📄 Exportar CSV', key='Exportar_CSV', **button_style)]
]

edit_form_layout = [[psg.Text(f'{headings[i]}:', size=(20, 1)), psg.InputText('', key=f'field_{i}', font=('Segoe UI', 10))] for i in range(len(headings))] + \
                   [[psg.Button('Atualizar', **button_style), psg.Button('Excluir', key='Excluir_Item', **button_style)]]

registration_layout = [[psg.Text('✏️ Registrar Monitoramento', font=header_font, text_color='#007ACC')]] + \
                     [[psg.Text(headings[i], size=(20, 1)), psg.InputText(key=f'reg_field_{i}', font=('Segoe UI', 10))] for i in range(len(headings))] + \
                     [[psg.Button('💾 Confirmar Registro', **button_style), psg.Button('Cancelar', key='Cancelar_Registro', **button_style)]]

# Função principal
def main_window(logged_user):
    layout = [
        [
         psg.Column(menu_layout, element_justification='center', pad=(10, 20), background_color='#007ACC'), psg.VerticalSeparator(),
         psg.Column(dashboard_layout, key='Dashboard_Section', visible=True),
         psg.Column(edit_form_layout, key='Edit_Section', visible=False),
         psg.Column(registration_layout, key='Register_Section', visible=False)
        ],
        [psg.Text(f'Usuário logado: {logged_user}', font=('Segoe UI', 10), text_color='#333333', pad=(10, 10))]
    ]
    window = psg.Window('LECOMPY - Dashboard', layout, resizable=True, finalize=True, background_color='#FFFFFF')
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
        # Verifica se todos os campos foram preenchidos
            if all(values.get(f'reg_field_{i}') for i in range(len(headings))):
                # Exibe os valores que estão sendo registrados
                print("Dados a serem inseridos:", [values[f'reg_field_{i}'] for i in range(len(headings))])

                # Realiza a inserção dos dados
                try:
                    insert_data(*[values[f'reg_field_{i}'] for i in range(len(headings))])
                    # Atualiza a tabela com os dados do banco de dados
                    data = fetch_all_data()
                    window['table_alias'].update(values=data)
                    psg.popup('Registro adicionado com sucesso!', title='Sucesso')
                    window['Dashboard_Section'].update(visible=True)
                    window['Register_Section'].update(visible=False)
                except Exception as e:
                    # Exibe erro caso haja um problema na inserção
                    print("Erro ao inserir dados:", e)
                    psg.popup(f"Erro ao registrar dados: {e}", title='Erro')
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

logged_user = login_window()
if logged_user:
    main_window(logged_user)
