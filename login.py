import PySimpleGUI as pygui
import sqlite3
import csv

# Configurações iniciais e layout dos menus
MENU_LAYOUT = [
    [pygui.Button('🏠 Dashboard', key='Dashboard', size=(20, 1), font=('Helvetica', 12))],
    [pygui.Button('👁 Visualizar', key='Visualizar', size=(20, 1), font=('Helvetica', 12))],
    [pygui.Button('➕ Registrar monitoramento', key='Registrar', size=(20, 1), font=('Helvetica', 12))],
    [pygui.Button('🚪 Desconectar', size=(20, 1), font=('Helvetica', 12), button_color=('white', '#d9534f'))]
]

HEADINGS = ['Código LECOM', 'OLT', 'ONT ou ONU', 'Roteador', 'FSAN/Nº série ONT ou ONU', 'Nº série Roteador', 'Início', 'Fim', 'Responsável', 'Status', 'Observações']

def connect_to_db(db_name="lecompy_data.db"):
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA busy_timeout = 5000")
    cursor = conn.cursor()
    return conn, cursor

def fetch_all_data():
    conn, cursor = connect_to_db()
    cursor.execute('SELECT codigo_lecom, olt, ont_ou_onu, roteador, fsan_serial_ont_onu, serial_roteador, inicio, fim, responsavel, status, observacoes FROM registros')
    rows = cursor.fetchall()
    conn.close()
    return rows

def create_users_table():
    conn, cursor = connect_to_db()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

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

def check_login(username, password):
    conn, cursor = connect_to_db()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def register_user(username, password):
    conn, cursor = connect_to_db()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def create_login_layout():
    return [
        [pygui.Text("Usuário"), pygui.InputText(key="username")],
        [pygui.Text("Senha"), pygui.InputText(key="password", password_char="*")],
        [pygui.Button("Login"), pygui.Button("Registrar"), pygui.Button("Sair")]
    ]

def create_register_layout():
    return [
        [pygui.Text("Novo Usuário"), pygui.InputText(key="new_username")],
        [pygui.Text("Nova Senha"), pygui.InputText(key="new_password", password_char="*")],
        [pygui.Button("Confirmar Cadastro"), pygui.Button("Cancelar")]
    ]

def create_dashboard_layout(data, username):
    return [
        [pygui.Text(f'Bem-vindo, {username}!', font=('Helvetica', 12), justification='left')],
        [pygui.Text('LECOMPY - Dashboard', font=('Helvetica', 12))],
        [pygui.Table(values=data, headings=HEADINGS, key='table_alias', justification='center', auto_size_columns=False,
                   display_row_numbers=False, col_widths=[15] * len(HEADINGS), row_height=30,
                   font=('Helvetica', 12), text_color='white', background_color='#1e1e2e', alternating_row_color='#2b2b3c',
                   header_text_color='white', header_background_color='#3a3a5b', selected_row_colors=('white', '#007bff'), vertical_scroll_only=False)],
        [pygui.Button('📄 Exportar CSV', size=(15, 1), key='Exportar_CSV', button_color=('white', '#5bc0de'))]
    ]

def create_registration_layout():
    return [
        [pygui.Text('Registrar Monitoramento', font=('Helvetica', 18))],
        [pygui.Text('Código LECOM', size=(15, 1)), pygui.InputText(key='codigo_lecom', size=(30, 1))],
        [pygui.Text('OLT', size=(15, 1)), pygui.Combo(['ZTE C350', 'ZTE C650', 'Zhone 219', 'Zhone 319', 'FiberHome 5', 'FiberHome 6', 'Huawei MA5800', 'Huawei MA5600', 'Nokia'], key='olt', size=(30, 1))],
        [pygui.Text('ONT ou ONU', size=(15, 1)), pygui.InputText(key='ont_ou_onu', size=(30, 1))],
        [pygui.Text('Roteador', size=(15, 1)), pygui.InputText(key='roteador', size=(30, 1), tooltip="Caso esteja provisionando com uma ONU Bridge, informar o modelo do roteador selecionado.")],
        [pygui.Text('FSAN/Nº série ONT/ONU', size=(15, 1)), pygui.InputText(key='fsan_serial_ont_onu', size=(30, 1))],
        [pygui.Text('Nº série Roteador', size=(15, 1)), pygui.InputText(key='serial_roteador', size=(30, 1))],
        [pygui.Text('Início', size=(15, 1)), pygui.InputText(key='inicio', size=(30, 1))],
        [pygui.Text('Fim', size=(15, 1)), pygui.InputText(key='fim', size=(30, 1))],
        [pygui.Text('Responsável', size=(15, 1)), pygui.Combo(['Bruno', 'Eslier', 'Elenir', 'Guilherme', 'Jean', 'Renato', 'Rhyan'], key='responsavel', size=(30, 1))],
        [pygui.Text('Status', size=(15, 1)), pygui.Combo(['Solicitado', 'Montado', 'Desmontado e finalizado'], key='status', size=(28, 1))],
        [pygui.Text('Observações', size=(15, 1)), pygui.Multiline(size=(30, 3), key='observacoes')],
        [pygui.Button('💾 Registrar', key='Confirmar_Registro', button_color=('white', '#5bc0de')), pygui.Button('Cancelar', key='Cancelar_Registro', button_color=('white', '#d9534f'))]
    ]

def login_screen():
    window = pygui.Window("Login", create_login_layout())
    while True:
        event, values = window.read()
        if event in (pygui.WINDOW_CLOSED, "Desconectar"):
            break
        elif event == "Login":
            if user := check_login(values["username"], values["password"]):
                return values["username"]
            else:
                pygui.popup("Usuário ou senha incorretos.", title="Erro")
        elif event == "Registrar":
            window.hide()
            if register_screen():
                pygui.popup("Usuário registrado com sucesso!", title="Sucesso")
            window.un_hide()
    window.close()
    return None

def register_screen():
    window = pygui.Window("Registrar Novo Usuário", create_register_layout())
    while True:
        event, values = window.read()
        if event in (pygui.WINDOW_CLOSED, "Cancelar"):
            break
        elif event == "Confirmar Cadastro":
            if values["new_username"] and values["new_password"]:
                if register_user(values["new_username"], values["new_password"]):
                    window.close()
                    return True
                else:
                    pygui.popup("Nome de usuário já existe. Escolha outro.", title="Erro")
            else:
                pygui.popup("Preencha todos os campos.", title="Erro")
    window.close()
    return False

def create_edit_section():
    # Criando dinamicamente os campos de edição (field_0, field_1, ...)
    edit_section = [
        [pygui.Text(f'{HEADINGS[i]}:', size=(15, 1)), pygui.InputText('', key=f'field_{i}', size=(30, 1))]
        for i in range(len(HEADINGS))
    ]
    edit_section.append([pygui.Button('Atualizar', key='Atualizar'), pygui.Button('Excluir', key='Excluir_Item', button_color=('white', '#d9534f'))])
    return edit_section

def main_window(username):
    data = fetch_all_data()
    layout = [
        [pygui.Column(MENU_LAYOUT, vertical_alignment='top'), pygui.VerticalSeparator(),
         pygui.Column(create_dashboard_layout(data, username), key='Dashboard_Section', visible=True),
         pygui.Column(create_registration_layout(), key='Register_Section', visible=False)]
    ]

    window = pygui.Window('LECOMPY - Dashboard', layout, size=(1000, 450), resizable=True, finalize=True)
    while True:
        event, values = window.read()

        if event == pygui.WINDOW_CLOSED or event == 'Sair':
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
            if all(values.get(f'reg_field_{i}') for i in range(len(HEADINGS))):
                insert_data(*[values[f'reg_field_{i}'] for i in range(len(HEADINGS))])
                data = fetch_all_data()
                window['table_alias'].update(values=data)
                pygui.popup('Registro adicionado com sucesso!', title='Sucesso')
                window['Dashboard_Section'].update(visible=True)
                window['Register_Section'].update(visible=False)
            else:
                pygui.popup('Preencha todos os campos!', title='Erro')

        elif event == 'Visualizar':
            selected_row_idx = values.get('table_alias', [0])
            if selected_row_idx:
                row_idx = selected_row_idx[0]
                selected_row_data = data[row_idx][1:]
                print('Linha inserida: ', selected_row_data)
                for i, val in enumerate(selected_row_data):
                    window[f'field_{i}'].update(val)
                window['Dashboard_Section'].update(visible=False)
                window['Edit_Section'].update(visible=True)

        elif event == 'Atualizar' and row_idx is not None:
            updated_values = [values[f'field_{i}'] for i in range(len(HEADINGS))]
            update_data(data[row_idx][0], *updated_values)
            data = fetch_all_data()
            window['table_alias'].update(values=data)
            pygui.popup('Registro atualizado com sucesso!', title='Sucesso')
            window['Dashboard_Section'].update(visible=True)
            window['Edit_Section'].update(visible=False)

        elif event == 'Excluir_Item' and row_idx is not None:
            delete_data(data[row_idx][0])
            data = fetch_all_data()
            window['table_alias'].update(values=data)
            pygui.popup('Registro excluído com sucesso!', title='Sucesso')
            window['Dashboard_Section'].update(visible=True)
            window['Edit_Section'].update(visible=False)

        elif event == 'Exportar_CSV':
            file_path = pygui.popup_get_file('Salvar como', save_as=True, default_extension='.csv', file_types=(("CSV Files", "*.csv"),))
            if file_path:
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(HEADINGS)
                    writer.writerows(data)
                pygui.popup('Arquivo CSV salvo com sucesso!', title='Sucesso')

    window.close()

if (username := login_screen()):
    main_window(username)
else:
    pygui.popup("Aplicativo encerrado.", title="Adeus")
