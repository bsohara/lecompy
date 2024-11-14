import sqlite3
import PySimpleGUI as sg
from datetime import datetime

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('lecompy_data.db')
cursor = conn.cursor()

# Função para criar as tabelas no banco de dados
def create_tables():
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT NOT NULL UNIQUE,
                        senha TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS equipamentos (
                        id_equipamento INTEGER PRIMARY KEY AUTOINCREMENT,
                        tipo TEXT,
                        ativo_desktop TEXT,
                        vendor TEXT,
                        modelo TEXT,
                        mac TEXT,
                        numero_serie TEXT,
                        fsan TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS registros (
                        id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_equipamento INTEGER,
                        id_usuario INTEGER,
                        descricao TEXT,
                        status TEXT,
                        data_inicio TEXT,
                        data_conclusao TEXT,
                        modificado_por INTEGER,
                        FOREIGN KEY (id_equipamento) REFERENCES equipamentos(id_equipamento),
                        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
                        FOREIGN KEY (modificado_por) REFERENCES usuarios(id_usuario))''')

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
    cursor.execute("SELECT id_usuario, usuario FROM usuarios WHERE usuario = ? AND senha = ?", (username, password))
    result = cursor.fetchone()
    return result if result else None

# Layout para a tela de login
def login_layout():
    layout = [
        [sg.Text('Usuário'), sg.InputText(key='-LOGIN_USER-')],
        [sg.Text('Senha'), sg.InputText(key='-LOGIN_PASS-', password_char='*')],
        [sg.Button('Login'), sg.Button('Cadastrar Usuário')]
    ]
    return layout

# Layout para o portal principal
def main_layout(username):
    equipment_layout = [
        [sg.Text('Tipo'), sg.Combo(['ONT', 'ONU', 'Roteador'], key='-TIPO-')],
        [sg.Text('Ativo Desktop'), sg.InputText(key='-DESKTOP-')],
        [sg.Text('Vendor'), sg.InputText(key='-VENDOR-')],
        [sg.Text('Modelo'), sg.InputText(key='-MODEL-')],
        [sg.Text('MAC'), sg.InputText(key='-MAC-')],
        [sg.Text('Número de Série'), sg.InputText(key='-SERIE-')],
        [sg.Text('FSAN'), sg.InputText(key='-FSAN-')],
        [sg.Button('Cadastrar Equipamento')]
    ]

    register_layout = [
        [sg.Text('Equipamento ID'), sg.InputText(key='-EQUIP_ID-')],
        [sg.Text('Descrição'), sg.InputText(key='-DESC-')],
        [sg.Text('Status'), sg.Combo(['Aberto', 'Em Progresso', 'Concluído'], key='-STATUS-')],
        [sg.Text('Data de Início (YYYY-MM-DD)'), sg.InputText(key='-START-')],
        [sg.Text('Data de Conclusão (YYYY-MM-DD)'), sg.InputText(key='-END-')],
        [sg.Button('Registrar'), sg.Button('Alterar Registro'), sg.Button('Deletar Registro')]
    ]

    view_layout = [
        [sg.Text(f'Usuário logado: {username}', key='-USER-')],
        [sg.Button('Mostrar Registros')],
        [sg.Table(values=[], headings=['ID', 'Equipamento ID', 'Descrição', 'Status', 'Início', 'Conclusão', 'Criado por', 'Modificado por'],
                  key='-REG_TABLE-', enable_events=True, auto_size_columns=True)],
    ]

    layout = [
        [sg.TabGroup([
            [sg.Tab('Visualizar Registros', view_layout),
            sg.Tab('Cadastrar Equipamento', equipment_layout), 
            sg.Tab('Gerenciar Registros', register_layout)]
        ])]
    ]
    return layout

# Janela principal
def main(user_id, username):
    sg.theme('LightBlue')
    window = sg.Window('Portal de Gerenciamento', main_layout(username))

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break

        # Cadastro de Equipamento
        if event == 'Cadastrar Equipamento':
            insert_data('equipamentos', {
                'tipo': values['-TIPO-'],
                'ativo_desktop': values['-DESKTOP-'],
                'vendor': values['-VENDOR-'],
                'modelo': values['-MODEL-'],
                'mac': values['-MAC-'],
                'numero_serie': values['-SERIE-'],
                'fsan': values['-FSAN-']
            })
            sg.popup('Equipamento cadastrado com sucesso!')

        # Registrar novo registro
        elif event == 'Registrar':
            insert_data('registros', {
                'id_equipamento': values['-EQUIP_ID-'],
                'id_usuario': user_id,
                'descricao': values['-DESC-'],
                'status': values['-STATUS-'],
                'data_inicio': values['-START-'],
                'data_conclusao': values['-END-'],
                'modificado_por': None
            })
            sg.popup('Registro cadastrado com sucesso!')

        # Alterar um registro existente
        elif event == 'Alterar Registro':
            cursor.execute('''UPDATE registros 
                              SET descricao = ?, status = ?, data_inicio = ?, data_conclusao = ?, modificado_por = ?
                              WHERE id_registro = ?''', 
                           (values['-DESC-'], values['-STATUS-'], values['-START-'], values['-END-'], user_id, values['-EQUIP_ID-']))
            conn.commit()
            sg.popup('Registro alterado com sucesso!')

        # Deletar um registro existente
        elif event == 'Deletar Registro':
            cursor.execute('DELETE FROM registros WHERE id_registro = ?', (values['-EQUIP_ID-'],))
            conn.commit()
            sg.popup('Registro deletado com sucesso!')

        # Mostrar registros
        elif event == 'Mostrar Registros':
            cursor.execute('''SELECT r.id_registro, r.id_equipamento, r.descricao, r.status, r.data_inicio, r.data_conclusao,
                                     u.usuario AS criado_por, um.usuario AS modificado_por
                              FROM registros r
                              JOIN usuarios u ON r.id_usuario = u.id_usuario
                              LEFT JOIN usuarios um ON r.modificado_por = um.id_usuario''')
            registros = cursor.fetchall()
            window['-REG_TABLE-'].update(registros)

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
            user_data = authenticate_user(values['-LOGIN_USER-'], values['-LOGIN_PASS-'])
            if user_data:
                user_id, username = user_data
                window.close()
                main(user_id, username)
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
