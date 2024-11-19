import sqlite3
import PySimpleGUI as sg
from datetime import datetime

# Conectar ao banco de dados SQLite
try:
    conn = sqlite3.connect('lecompy_data.db')
    cursor = conn.cursor()
except sqlite3.Error as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
    exit(1)

# Função para criar as tabelas e views no banco de dados
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
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_registros_id_equipamento ON registros(id_equipamento)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_registros_id_usuario ON registros(id_usuario)")

    # Criar views
    cursor.execute('''CREATE VIEW IF NOT EXISTS vw_registros AS
                      SELECT r.id_registro, e.tipo AS equipamento, e.ativo_desktop AS ativo, e.fsan, 
                             r.descricao, r.status, r.data_inicio, r.data_conclusao
                      FROM registros r
                      JOIN equipamentos e ON r.id_equipamento = e.id_equipamento''')

    cursor.execute('''CREATE VIEW IF NOT EXISTS vw_equipamentos AS
                      SELECT e.id_equipamento, e.tipo AS equipamento, e.modelo, e.vendor, 
                             e.mac, e.numero_serie, e.fsan
                      FROM equipamentos e''')

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

# Função para exibir registros na tabela
def show_registros(window):
    cursor.execute('SELECT * FROM vw_registros')
    registros = cursor.fetchall()
    window['-TABLE-'].update(values=registros, headings=['ID', 'Equipamento', 'Ativo', 'FSAN', 'Descrição', 'Status', 'Data Início', 'Data Fim'])

# Função para exibir equipamentos na tabela
def show_equipamentos(window):
    cursor.execute('SELECT * FROM vw_equipamentos')
    equipamentos = cursor.fetchall()
    window['-TABLE-'].update(values=equipamentos, headings=['ID', 'Equipamento', 'Modelo', 'Vendor', 'MAC', 'Número de Série', 'FSAN'])

# Função para gerar layout das abas
def main_layout(username):
    # Layout para a aba de Visualização
    tab1_layout = [
        [sg.Button('Visualizar Registros')],
        [sg.Button('Visualizar Equipamentos')],
        [sg.Table(values=[], headings=[], key='-TABLE-')]
    ]
    
    # Layout para a aba de Cadastro/Alteração de Registros
    tab2_layout = [
        [sg.Text('Cadastrar Registro')],
        [sg.Text('Equipamento ID'), sg.InputText(key=' -EQUIP_ID_REG-')],
        [sg.Text('Descrição'), sg.InputText(key='-DESC_REG-')],
        [sg.Text('Status'), sg.Combo(['Solicitado', 'Montado', 'Desmontado e finalizado'], key='-STATUS_REG-')],
        [sg.Text('Data de Início (YYYY-MM-DD)'), sg.InputText(key='-START_REG-')],
        [sg.Text('Data de Conclusão (YYYY-MM-DD)'), sg.InputText(key='-END_REG-')],
        [sg.Button('Salvar Registro'), sg.Button('Alterar Registro')]
    ]

    # Layout para a aba de Cadastro/Alteração de Equipamentos
    tab3_layout = [
        [sg.Text('Cadastrar Equipamento')],
        [sg.Text('Tipo'), sg.Combo(['ONT', 'ONU', 'Roteador'], key='-TIPO_EQUIP-')],
        [sg.Text('Ativo Desktop'), sg.InputText(key='-DESKTOP_EQUIP-')],
        [sg.Text('Vendor'), sg.InputText(key='-VENDOR_EQUIP-')],
        [sg.Text('Modelo'), sg.InputText(key='-MODEL_EQUIP-')],
        [sg.Text('MAC'), sg.InputText(key='-MAC_EQUIP-')],
        [sg.Text('Número de Série'), sg.InputText(key='-SERIE_EQUIP-')],
        [sg.Text('FSAN'), sg.InputText(key='-FSAN_EQUIP-')],
        [sg.Button('Salvar Equipamento'), sg.Button('Alterar Equipamento')]
    ]

    # Layout com as abas
    layout = [
        [sg.TabGroup([
            [sg.Tab('Visualização', tab1_layout),
             sg.Tab('Cadastro/Alteração Registros', tab2_layout),
             sg.Tab('Cadastro/Alteração Equipamentos', tab3_layout)]
        ])]
    ]
    return layout

# Função para salvar registro
def save_registro(user_id, equip_id, descricao, status, data_inicio, data_conclusao):
    insert_data('registros', {
        'id_equipamento': equip_id,
        'id_usuario': user_id,
        'descricao': descricao,
        'status': status,
        'data_inicio': data_inicio,
        'data_conclusao': data_conclusao,
        'modificado_por': None
    })
    sg.popup('Registro cadastrado com sucesso!')

# Função para atualizar registro
def update_registro(user_id, reg_id, descricao, status, data_inicio, data_conclusao):
    cursor.execute('''UPDATE registros 
                      SET descricao = ?, status = ?, data_inicio = ?, data_conclusao = ?, modificado_por = ?
                      WHERE id_registro = ?''', 
                   (descricao, status, data_inicio, data_conclusao, user_id, reg_id))
    conn.commit()
    sg.popup('Registro alterado com sucesso!')

# Função para salvar equipamento
def save_equipamento(tipo, ativo_desktop, vendor, modelo, mac, numero_serie, fsan):
    insert_data('equipamentos', {
        'tipo': tipo,
        'ativo_desktop': ativo_desktop,
        'vendor': vendor,
        'modelo': modelo,
        'mac': mac,
        'numero_serie': numero_serie,
        'fsan': fsan
    })
    sg.popup('Equipamento cadastrado com sucesso!')

# Função para atualizar equipamento
def update_equipamento(equip_id, tipo, ativo_desktop, vendor, modelo, mac, numero_serie, fsan):
    cursor.execute('''UPDATE equipamentos 
                      SET tipo = ?, ativo_desktop = ?, vendor = ?, modelo = ?, mac = ?, numero_serie = ?, fsan = ?
                      WHERE id_equipamento = ?''', 
                   (tipo, ativo_desktop, vendor, modelo, mac, numero_serie, fsan, equip_id))
    conn.commit()
    sg.popup('Equipamento alterado com sucesso!')

# Janela principal com abas
def main(user_id, username):
    sg.theme('LightBlue')
    window = sg.Window('Portal de Gerenciamento', main_layout(username))

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break

        # Visualizar Registros
        if event == 'Visualizar Registros':
            show_registros(window)

        # Visualizar Equipamentos
        if event == 'Visualizar Equipamentos':
            show_equipamentos(window)

        # Salvar Registro
        if event == 'Salvar Registro':
            save_registro(user_id, values['-EQUIP_ID_REG-'], values['-DESC_REG-'], values['-STATUS_REG-'], values['-START_REG-'], values['-END_REG-'])

        # ```python
        # Alterar Registro
        if event == 'Alterar Registro':
            update_registro(user_id, values['-REG_ID-'], values['-DESC_REG-'], values['-STATUS_REG-'], values['-START_REG-'], values['-END_REG-'])

        # Salvar Equipamento
        if event == 'Salvar Equipamento':
            save_equipamento(values['-TIPO_EQUIP-'], values['-DESKTOP_EQUIP-'], values['-VENDOR_EQUIP-'], values['-MODEL_EQUIP-'], values['-MAC_EQUIP-'], values['-SERIE_EQUIP-'], values['-FSAN_EQUIP-'])

        # Alterar Equipamento
        if event == 'Alterar Equipamento':
            update_equipamento(values['-EQUIP_ID-'], values['-TIPO_EQUIP-'], values['-DESKTOP_EQUIP-'], values['-VENDOR_EQUIP-'], values['-MODEL_EQUIP-'], values['-MAC_EQUIP-'], values['-SERIE_EQUIP-'], values['-FSAN_EQUIP-'])

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