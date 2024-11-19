import sqlite3
import tabulate
import PySimpleGUI as sg
from datetime import datetime

# Conectar ao banco de dados SQLite
try:
    conn = sqlite3.connect('lecompy_data.db')
    cursor = conn.cursor()
except sqlite3.Error as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
    exit(1)

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
                        data_inicio DATE,
                        data_conclusao DATE,
                        modificado_por INTEGER,
                        FOREIGN KEY (id_equipamento) REFERENCES equipamentos(id_equipamento),
                        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
                        FOREIGN KEY (modificado_por) REFERENCES usuarios(id_usuario))''')

    # Adicionar índices
    cursor.execute("CREATE INDEX idx_registros_id_equipamento ON registros(id_equipamento)")
    cursor.execute("CREATE INDEX idx_registros_id_usuario ON registros(id_usuario)")

    conn.commit()

# Função para inserir dados nas tabelas
def insert_data(table, values):
    columns = ', '.join(values.keys())
    placeholders = ', '.join(['?'] * len(values))
    sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
    try:
        cursor.execute(sql, tuple(values.values()))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Erro ao inserir dados: {e}")

# Função para autenticar usuário
def authenticate_user(username, password):
    cursor.execute("SELECT id_usuario, usuario FROM usuarios WHERE usuario =? AND senha =?", (username, password))
    return cursor.fetchone()

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
    left_column = [
        [sg.Button('Visualizar Registros')],
        [sg.Button('Cadastrar Equipamento')],
        [sg.Button('Gerenciar Registros')],
        [sg.Button('Logout')]
    ]

    right_column = [
        [sg.Text(f'Usuário logado: {username}')],
        [sg.Multiline(size=(40, 20), key='-OUTPUT-')]
    ]

    layout = [
        [sg.Column(left_column, element_justification='left'),
         sg.VSeparator(),
         sg.Column(right_column, element_justification='right')]
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

        if event == 'Logout':
            window.close()
            login_screen()

        if event == 'Visualizar Registros':
            cursor.execute('''SELECT r.id_registro, r.id_equipamento, r.descricao, r.status, r.data_inicio, r.data_conclusao,
                                     u.usuario AS criado_por, um.usuario AS modificado_por
                              FROM registros r
                              JOIN usuarios u ON r.id_usuario = u.id_usuario
                              LEFT JOIN usuarios um ON r.modificado_por = um.id_usuario''')
            registros = cursor.fetchall()
            output = tabulate.tabulate(registros, headers=['ID Registro', 'ID Equipamento', 'Descrição', 'Status', 'Data Início', 'Data Conclusão', 'Criado por', 'Modificado por'], tablefmt='grid')
            window['-OUTPUT-'].update(output)

        if event == 'Cadastrar Equipamento':
            equip_window = sg.Window('Cadastrar Equipamento', [
                [sg.Text('Tipo'), sg.Combo(['ONT', 'ONU', 'Roteador'], key='-TIPO-')],
                [sg.Text('Ativo Desktop'), sg.InputText(key='-DESKTOP-')],
                [sg.Text('Vendor'), sg.InputText(key='-VENDOR-')],
                [sg.Text('Modelo'), sg.InputText(key='-MODEL-')],
                [sg.Text('MAC'), sg.InputText(key='-MAC-')],
                [sg.Text('Número de Série'), sg.InputText(key='-SERIE-')],
                [sg.Text('FSAN'), sg.InputText(key='-FSAN-')],
                [sg.Button('Salvar'), sg.Button('Cancelar')]
            ])
            
            while True:
                ev, vals = equip_window.read()
                if ev == 'Salvar':
                    insert_data('equipamentos', {
                        'tipo': vals['-TIPO-'],
                        'ativo_desktop': vals['-DESKTOP-'],
                        'vendor': vals['-VENDOR-'],
                        'modelo': vals['-MODEL-'],
                        'mac': vals['-MAC-'],
                        'numero_serie': vals['-SERIE-'],
                        'fsan': vals['-FSAN-']
                    })
                    sg.popup('Equipamento cadastrado com sucesso!')
                    equip_window.close()
                    break
                elif ev == 'Cancelar' or ev == sg.WINDOW_CLOSED:
                    equip_window.close()
                    break

        if event == 'Gerenciar Registros':
            reg_window = sg.Window('Gerenciar Registros', [
                [sg.Text('Equipamento ID'), sg.InputText(key='-EQUIP_ID-')],
                [sg.Text('Descrição'), sg.InputText(key='-DESC-')],
                [sg.Text('Status'), sg.Combo(['Aberto', 'Em Progresso', 'Concluído'], key='-STATUS-')],
                [sg.Text('Data de Início (YYYY-MM-DD)'), sg.InputText(key='-START-')],
                [sg.Text('Data de Conclusão (YYYY-MM-DD)'), sg.InputText(key='-END-')],
                [sg.Button('Registrar'), sg.Button('Alterar'), sg.Button('Deletar')]
            ])

            while True:
                reg_ev, reg_vals = reg_window.read()
                if reg_ev == 'Registrar':
                    insert_data('registros', {
                        'id_equipamento': reg_vals['-EQUIP_ID-'],
                        'id_usuario': user_id,
                        'descricao': reg_vals['-DESC-'],
                        'status': reg_vals['-STATUS-'],
                        'data_inicio': reg_vals['-START-'],
                        'data_conclusao': reg_vals['-END-'],
                        'modificado_por': None
                    })
                    sg.popup('Registro cadastrado com sucesso!')
                elif reg_ev == 'Alterar':
                    cursor.execute('''UPDATE registros 
                                      SET descricao = ?, status = ?, data_inicio = ?, data_conclusao = ?, modificado_por = ?
                                      WHERE id_registro = ?''', 
                                   (reg_vals['-DESC-'], reg_vals['-STATUS-'], reg_vals['-START-'], reg_vals['-END-'], user_id, reg_vals['-EQUIP_ID-']))
                    conn.commit()
                    sg.popup('Registro alterado com sucesso!')
                elif reg_ev == 'Deletar':
                    cursor.execute('DELETE FROM registros WHERE id_registro = ?', (reg_vals['-EQUIP_ID-'],))
                    conn.commit()
                    sg.popup('Registro deletado com sucesso!')
                elif reg_ev == sg.WINDOW_CLOSED:
                    reg_window.close()
                    break

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