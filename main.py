import sqlite3
import PySimpleGUI as sg
from datetime import datetime

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('lecompy_data.db')
cursor = conn.cursor()

# Criar tabelas no banco de dados
def create_tables():
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT NOT NULL UNIQUE,
                        senha TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS ont (
                        id_ont INTEGER PRIMARY KEY AUTOINCREMENT,
                        ativo_desktop TEXT,
                        vendor TEXT,
                        modelo TEXT,
                        mac TEXT,
                        numero_serie TEXT,
                        fsan TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS onu (
                        id_onu INTEGER PRIMARY KEY AUTOINCREMENT,
                        ativo_desktop TEXT,
                        vendor TEXT,
                        modelo TEXT,
                        mac TEXT,
                        numero_serie TEXT,
                        fsan TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS roteador (
                        id_roteador INTEGER PRIMARY KEY AUTOINCREMENT,
                        ativo_desktop TEXT,
                        vendor TEXT,
                        modelo TEXT,
                        mac TEXT,
                        numero_serie TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS registro_ont (
                        id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_ont INTEGER,
                        id_usuario INTEGER,
                        data_inicio TEXT,
                        data_conclusao TEXT,
                        descricao_chamado TEXT,
                        data_chamado TEXT,
                        FOREIGN KEY (id_ont) REFERENCES ont(id_ont),
                        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS registro_onu_roteador (
                        id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_onu INTEGER,
                        id_roteador INTEGER,
                        id_usuario INTEGER,
                        data_inicio TEXT,
                        data_conclusao TEXT,
                        descricao_chamado TEXT,
                        data_chamado TEXT,
                        FOREIGN KEY (id_onu) REFERENCES onu(id_onu),
                        FOREIGN KEY (id_roteador) REFERENCES roteador(id_roteador),
                        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario))''')

    conn.commit()

# Função para inserir dados nas tabelas
def insert_data(table, values):
    columns = ', '.join(values.keys())
    placeholders = ', '.join(['?'] * len(values))
    sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
    cursor.execute(sql, tuple(values.values()))
    conn.commit()

# Função para autenticar usuário
def authenticate_user(username, password):
    cursor.execute("SELECT id_usuario FROM usuarios WHERE usuario = ? AND senha = ?", (username, password))
    result = cursor.fetchone()
    return result[0] if result else None

# Layout para a tela de login
def login_layout():
    layout = [
        [sg.Text('Usuário'), sg.InputText(key='-LOGIN_USER-')],
        [sg.Text('Senha'), sg.InputText(key='-LOGIN_PASS-', password_char='*')],
        [sg.Button('Login'), sg.Button('Cadastrar Usuário')]
    ]
    return layout

# Layout para o portal principal
def main_layout():
    tab1_layout = [
        [sg.Text('Ativo Desktop'), sg.InputText(key='-DESKTOP-')],
        [sg.Text('Vendor'), sg.InputText(key='-VENDOR-')],
        [sg.Text('Modelo'), sg.InputText(key='-MODEL-')],
        [sg.Text('MAC'), sg.InputText(key='-MAC-')],
        [sg.Text('Número de Série'), sg.InputText(key='-SERIE-')],
        [sg.Text('FSAN'), sg.InputText(key='-FSAN-')],
        [sg.Button('Cadastrar ONT'), sg.Button('Cadastrar ONU'), sg.Button('Cadastrar Roteador')]
    ]

    tab2_layout = [
        [sg.Text('ID da ONT'), sg.InputText(key='-ONT-ID-')],
        [sg.Text('Data de Início (YYYY-MM-DD)'), sg.InputText(key='-START-')],
        [sg.Text('Data de Conclusão (YYYY-MM-DD)'), sg.InputText(key='-END-')],
        [sg.Text('Descrição do Chamado LECOM'), sg.InputText(key='-DESC-CHAMADO-')],
        [sg.Button('Registrar ONT')]
    ]

    tab3_layout = [
        [sg.Text('ID da ONU'), sg.InputText(key='-ONU-ID-')],
        [sg.Text('ID do Roteador'), sg.InputText(key='-ROUTER-ID-')],
        [sg.Text('Data de Início (YYYY-MM-DD)'), sg.InputText(key='-START-ROUTER-')],
        [sg.Text('Data de Conclusão (YYYY-MM-DD)'), sg.InputText(key='-END-ROUTER-')],
        [sg.Text('Descrição do Chamado LECOM'), sg.InputText(key='-DESC-CHAMADO-ROUTER-')],
        [sg.Button('Registrar ONU e Roteador')]
    ]

    tab5_layout = [
        [sg.Text('Consultar Registros')],
        [sg.Button('Mostrar Registros ONT'), sg.Button('Mostrar Registros ONU e Roteador')],
        [sg.Table(values=[], headings=['ID', 'Vendor', 'Modelo', 'Data Início', 'Data Conclusão', 'Chamado'],
                  key='-TABLE-', auto_size_columns=True, display_row_numbers=False)]
    ]

    layout = [
        [sg.TabGroup([[sg.Tab('Equipamentos', tab1_layout),
                       sg.Tab('Registro ONT', tab2_layout),
                       sg.Tab('Registro ONU + Roteador', tab3_layout),
                       sg.Tab('Consultas', tab5_layout)]])],
    ]
    
    return layout

# Janela principal
def main(user_id):
    sg.theme('LightBlue')
    window = sg.Window('Portal de Gerenciamento', main_layout())

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break

        # Cadastro de ONT, ONU e Roteador
        if event == 'Cadastrar ONT':
            insert_data('ont', {
                'ativo_desktop': values['-DESKTOP-'],
                'vendor': values['-VENDOR-'],
                'modelo': values['-MODEL-'],
                'mac': values['-MAC-'],
                'numero_serie': values['-SERIE-'],
                'fsan': values['-FSAN-']
            })
            sg.popup('ONT cadastrada com sucesso!')

        elif event == 'Cadastrar ONU':
            insert_data('onu', {
                'ativo_desktop': values['-DESKTOP-'],
                'vendor': values['-VENDOR-'],
                'modelo': values['-MODEL-'],
                'mac': values['-MAC-'],
                'numero_serie': values['-SERIE-'],
                'fsan': values['-FSAN-']
            })
            sg.popup('ONU cadastrada com sucesso!')

        elif event == 'Cadastrar Roteador':
            insert_data('roteador', {
                'ativo_desktop': values['-DESKTOP-'],
                'vendor': values['-VENDOR-'],
                'modelo': values['-MODEL-'],
                'mac': values['-MAC-'],
                'numero_serie': values['-SERIE-']
            })
            sg.popup('Roteador cadastrado com sucesso!')

        # Registro ONT
        elif event == 'Registrar ONT':
            insert_data('registro_ont', {
                'id_ont': values['-ONT-ID-'],
                'id_usuario': user_id,
                'data_inicio': values['-START-'],
                'data_conclusao': values['-END-'],
                'descricao_chamado': values['-DESC-CHAMADO-'],
                'data_chamado': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            sg.popup('Registro de ONT realizado com sucesso!')

        # Registro ONU e Roteador
        elif event == 'Registrar ONU e Roteador':
            insert_data('registro_onu_roteador', {
                'id_onu': values['-ONU-ID-'],
                'id_roteador': values['-ROUTER-ID-'],
                'id_usuario': user_id,
                'data_inicio': values['-START-ROUTER-'],
                'data_conclusao': values['-END-ROUTER-'],
                'descricao_chamado': values['-DESC-CHAMADO-ROUTER-'],
                'data_chamado': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            sg.popup('Registro de ONU e Roteador realizado com sucesso!')

        # Mostrar Registros ONT
        elif event == 'Mostrar Registros ONT':
            cursor.execute('''SELECT r.id_registro, o.vendor, o.modelo, r.data_inicio, r.data_conclusao, r.descricao_chamado 
                              FROM registro_ont r
                              JOIN ont o ON r.id_ont = o.id_ont''')
            registros = cursor.fetchall()
            window['-TABLE-'].update(registros)

        # Mostrar Registros ONU e Roteador
        elif event == 'Mostrar Registros ONU e Roteador':
            cursor.execute('''SELECT r.id_registro, o.vendor, o.modelo, ro.modelo, r.data_inicio, r.data_conclusao, r.descricao_chamado
                              FROM registro_onu_roteador r
                              JOIN onu o ON r.id_onu = o.id_onu
                              JOIN roteador ro ON r.id_roteador = ro.id_roteador''')
            registros = cursor.fetchall()
            window['-TABLE-'].update(registros)

    window.close()

# Tela de login
def login_screen():
    sg.theme('LightBlue')
    window = sg.Window('Login', login_layout())

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break

        elif event == 'Login':
            user_id = authenticate_user(values['-LOGIN_USER-'], values['-LOGIN_PASS-'])
            if user_id:
                window.close()
                main(user_id)
            else:
                sg.popup('Usuário ou senha inválidos!')

        elif event == 'Cadastrar Usuário':
            insert_data('usuarios', {
                'usuario': values['-LOGIN_USER-'],
                'senha': values['-LOGIN_PASS-']
            })
            sg.popup('Usuário cadastrado com sucesso!')

    window.close()

# Inicializar o banco de dados e iniciar a tela de login
if __name__ == '__main__':
    create_tables()
    login_screen()
    conn.close()
