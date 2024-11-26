import sqlite3
import PySimpleGUI as sg
from datetime import datetime

# Função para criar o banco de dados e as tabelas
def create_database():
    connection = sqlite3.connect("lecompy_data.db")
    cursor = connection.cursor()

    # Tabela de usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)

    # Tabela de equipamentos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS equipamentos (
        id_equipamento INTEGER PRIMARY KEY AUTOINCREMENT,
        ativo TEXT NOT NULL,
        vendor TEXT NOT NULL,
        modelo TEXT NOT NULL,
        tipo TEXT CHECK(tipo IN ('ONU', 'ONT', 'roteador')) NOT NULL,
        mac TEXT NOT NULL,
        numero_serie TEXT NOT NULL,
        fsan TEXT NOT NULL
    )
    """)

    # Tabela de registros de chamados
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registros (
        id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
        id_equipamento INTEGER NOT NULL,
        chamado_lecom TEXT NOT NULL,
        data_inicio DATE,
        data_conclusao DATE,
        status TEXT CHECK(status IN ('Solicitado', 'Montado', 'Desmontado')) NOT NULL,
        responsavel TEXT NOT NULL,
        modificado_por TEXT,
        FOREIGN KEY (id_equipamento) REFERENCES equipamentos (id_equipamento)
    )
    """)

    connection.commit()
    connection.close()

# Criar banco de dados
create_database()

# Função para registrar um novo usuário
def register_user(username, password):
    connection = sqlite3.connect("lecompy_data.db")
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        connection.commit()
        sg.popup("Usuário registrado com sucesso!", title="Sucesso")
    except sqlite3.IntegrityError:
        sg.popup_error("O nome de usuário já existe!", title="Erro")
    finally:
        connection.close()

# Função para autenticar usuário
def authenticate_user(username, password):
    connection = sqlite3.connect("lecompy_data.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    connection.close()

    return user

# Interface de login
def login_screen():
    layout = [
        [sg.Text("Usuário:", size=(10, 1)), sg.Input(key="-USERNAME-", size=(30, 1))],
        [sg.Text("Senha:", size=(10, 1)), sg.Input(key="-PASSWORD-", password_char="*", size=(30, 1))],
        [sg.Button("Entrar"), sg.Button("Registrar")]
    ]

    window = sg.Window("Login", layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Cancelar"):
            break
        elif event == "Entrar":
            user = authenticate_user(values["-USERNAME-"], values["-PASSWORD-"])
            if user:
                window.close()
                main_screen(values["-USERNAME-"])  # Passa o nome do usuário logado
            else:
                sg.popup_error("Usuário ou senha inválidos.")
        elif event == "Registrar":
            username = values["-USERNAME-"]
            password = values["-PASSWORD-"]
            if username and password:
                register_user(username, password)
            else:
                sg.popup_error("Preencha os campos para registrar.")

    window.close()

def alterar_chamado(modificado_por):
    connection = sqlite3.connect("lecompy_data.db")
    cursor = connection.cursor()

    # Obter registros existentes
    cursor.execute("""
    SELECT r.id_registro, e.ativo, e.mac, r.chamado_lecom, r.data_inicio, r.data_conclusao, r.status, r.responsavel 
    FROM registros r
    JOIN equipamentos e ON r.id_equipamento = e.id_equipamento
    """)
    registros = cursor.fetchall()

    if not registros:
        sg.popup_error("Nenhum chamado disponível para alteração.")
        return

    # Layout para selecionar registro e alterar
    layout = [
        [sg.Text("Selecione o Chamado:")],
        [sg.Combo([f"{reg[0]} - {reg[1]} - {reg[3]} - {reg[6]}" for reg in registros], key="-REGISTRO-", size=(60, 1))],
        [sg.Text("Novo Status:"), sg.Combo(["Solicitado", "Montado", "Desmontado"], key="-NOVO_STATUS-")],
        [sg.Button("Salvar"), sg.Button("Cancelar")]
    ]

    window = sg.Window("Alterar Chamado", layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Cancelar"):
            break
        elif event == "Salvar":
            registro_selecionado = values["-REGISTRO-"]
            if not registro_selecionado:
                sg.popup_error("Selecione um chamado!")
                continue

            id_registro = int(registro_selecionado.split(" - ")[0])
            novo_status = values["-NOVO_STATUS-"]

            cursor.execute("""
            UPDATE registros
            SET status = ?, modificado_por = ?
            WHERE id_registro = ?
            """, (novo_status, modificado_por, id_registro))
            connection.commit()

            sg.popup("Chamado alterado com sucesso!")
            break

    connection.close()
    window.close()

# Página principal: Equipamentos e Chamados
def main_screen(username):
    equipamentos = atualizar_tabela_equipamentos()
    chamados = atualizar_tabela_chamados()

    layout = [
        [sg.Text(f"Usuário logado: {username}", size=(40, 1), justification="left")],
        [sg.TabGroup([
            [sg.Tab("Equipamentos", [
                [sg.Button("Adicionar Equipamento")],
                [sg.Table(values=equipamentos, headings=["ID", "Ativo", "Vendor", "Modelo", "Tipo", "MAC", "Nº Série", "FSAN"], 
                          key="-EQUIP_TABLE-", auto_size_columns=False, justification="center", num_rows=10)],
                [sg.Button("Excluir Equipamento", key="-EXCLUIR_EQUIP-")]
            ])],
            [sg.Tab("Chamados", [
                [sg.Button("Registrar Chamado"), sg.Button("Alterar Chamado")],
                [sg.Table(values=chamados, headings=["Chamado LECOM", "Ativo", "MAC", "Nº Série", "FSAN", "Início", "Fim", "Status", "Responsável", "Modificado Por"], 
                          key="-CHAMADOS_TABLE-", auto_size_columns=False, justification="center", num_rows=10)],
                [sg.Button("Excluir Chamado", key="-EXCLUIR_CHAMADO-")]
            ])]
        ])],
        [sg.Button("Sair")]
    ]

    window = sg.Window("Página Principal", layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Sair"):
            break
        elif event == "Adicionar Equipamento":
            add_equipamento()
            equipamentos = atualizar_tabela_equipamentos()  # Atualiza a lista de equipamentos
            window["-EQUIP_TABLE-"].update(values=equipamentos)
        elif event == "Registrar Chamado":
            registrar_chamado(username)
            chamados = atualizar_tabela_chamados()  # Atualiza a lista de chamados
            window["-CHAMADOS_TABLE-"].update(values=chamados)
        elif event == "Alterar Chamado":
            alterar_chamado(username)
            chamados = atualizar_tabela_chamados()  # Atualiza a lista de chamados
            window["-CHAMADOS_TABLE-"].update(values=chamados)
        elif event == "-EXCLUIR_EQUIP-":
            excluir_equipamento(window, equipamentos)
            equipamentos = atualizar_tabela_equipamentos()  # Atualiza a lista de equipamentos
            window["-EQUIP_TABLE-"].update(values=equipamentos)
        elif event == "-EXCLUIR_CHAMADO-":
            excluir_chamado(window, chamados)
            chamados = atualizar_tabela_chamados()  # Atualiza a lista de chamados
            window["-CHAMADOS_TABLE-"].update(values=chamados)
        elif event == "Sair":
            window.close()
            login_screen()
            break

    window.close()

# Função para adicionar um novo equipamento
def add_equipamento():
    layout = [
        [sg.Text("Ativo:"), sg.Input(key="-ATIVO-")],
        [sg.Text("Vendor:"), sg.Input(key="-VENDOR-")],
        [sg.Text("Modelo:"), sg.Input(key="-MODELO-")],
        [sg.Text("Tipo:"), sg.Combo(["ONU", "ONT", "roteador"], key="-TIPO-")],
        [sg.Text("MAC:"), sg.Input(key="-MAC-")],
        [sg.Text("Nº Série:"), sg.Input(key="-SERIE-")],
        [sg.Text("FSAN:"), sg.Input(key="-FSAN-")],
        [sg.Button("Salvar"), sg.Button("Cancelar")]
    ]

    window = sg.Window("Adicionar Equipamento", layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Cancelar"):
            break
        elif event == "Salvar":
            connection = sqlite3.connect("lecompy_data.db")
            cursor = connection.cursor()

            cursor.execute("""
            INSERT INTO equipamentos (ativo, vendor, modelo, tipo, mac, numero_serie, fsan) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (values["-ATIVO-"], values["-VENDOR-"], values["-MODELO-"], values["-TIPO-"], values["-MAC-"], values["-SERIE-"], values["-FSAN-"]))
            connection.commit()
            connection.close()
            sg.popup("Equipamento registrado com sucesso!")
            break

    window.close()

# Função para excluir equipamento
def excluir_equipamento(window, equipamentos):
    selecionado = window["-EQUIP_TABLE-"].get()
    if selecionado:
        # Pegue o índice da linha selecionada
        linha_selecionada = selecionado[0]  # Apenas o primeiro índice, já que é possível selecionar uma linha por vez
        
        if linha_selecionada is not None:
            # Pegue os dados da linha selecionada (completa)
            id_equipamento = equipamentos[linha_selecionada][0]  # Pegue a ID do equipamento, que é a primeira coluna

            # Confirme a exclusão
            confirmar = sg.popup_yes_no(f"Deseja excluir o equipamento com ID {id_equipamento}?")
            if confirmar == "Yes":
                connection = sqlite3.connect("lecompy_data.db")
                cursor = connection.cursor()
                cursor.execute("DELETE FROM equipamentos WHERE id_equipamento = ?", (id_equipamento,))
                connection.commit()
                connection.close()
                sg.popup("Equipamento excluído com sucesso!")
        else:
            sg.popup_error("Nenhuma linha selecionada para exclusão!")


# Função para registrar um chamado
def registrar_chamado(responsavel):
    connection = sqlite3.connect("lecompy_data.db")
    cursor = connection.cursor()
    
    # Obter equipamentos cadastrados
    cursor.execute("SELECT * FROM equipamentos")
    equipamentos = cursor.fetchall()

    # Criação da interface gráfica para registro do chamado
    equipamentos_list = [f"{equip[0]} - {equip[1]}" for equip in equipamentos]
    layout = [
        [sg.Text("Equipamento:")],
        [sg.Combo(equipamentos_list, key="-EQUIPAMENTO-")],
        [sg.Text("Chamado LECOM:"), sg.Input(key="-CHAMADO-")],
        [sg.Text("Data Início:"), sg.Input(key="-DATA_INICIO-", default_text=datetime.now().strftime("%Y-%m-%d"))],
        [sg.Text("Data Conclusão:"), sg.Input(key="-DATA_CONCLUSAO-")],  # Novo campo de Data Conclusão
        [sg.Text("Status:"), sg.Combo(["Solicitado", "Montado", "Desmontado"], key="-STATUS-")],
        [sg.Button("Salvar"), sg.Button("Cancelar")]
    ]

    window = sg.Window("Registrar Chamado", layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Cancelar"):
            break
        elif event == "Salvar":
            equipamento_selecionado = values["-EQUIPAMENTO-"]
            if not equipamento_selecionado:
                sg.popup_error("Selecione um equipamento!")
                continue

            id_equipamento = int(equipamento_selecionado.split(" - ")[0])
            chamado_lecom = values["-CHAMADO-"]
            data_inicio = values["-DATA_INICIO-"]
            data_conclusao = values["-DATA_CONCLUSAO-"]  # Obter a Data de Conclusão
            status = values["-STATUS-"]

            # Inserir no banco de dados
            cursor.execute("""
            INSERT INTO registros (id_equipamento, chamado_lecom, data_inicio, data_conclusao, status, responsavel)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (id_equipamento, chamado_lecom, data_inicio, data_conclusao, status, responsavel))
            connection.commit()
            sg.popup("Chamado registrado com sucesso!")
            break

    connection.close()
    window.close()


# Função para excluir chamado
def excluir_chamado(window, chamados):
    selecionado = window["-CHAMADOS_TABLE-"].get()
    if selecionado:
        # Pegue o índice da linha selecionada
        linha_selecionada = selecionado[0]  # Apenas o primeiro índice, já que é possível selecionar uma linha por vez

        # Verifique se a linha selecionada é válida
        if linha_selecionada is not None:
            # Pegue os dados da linha selecionada
            chamado_lecom = chamados[linha_selecionada][0]  # A primeira coluna do chamado LECOM

            # Confirme a exclusão
            confirmar = sg.popup_yes_no(f"Deseja excluir o chamado LECOM: {chamado_lecom}?")
            if confirmar == "Yes":
                connection = sqlite3.connect("lecompy_data.db")
                cursor = connection.cursor()
                cursor.execute("DELETE FROM registros WHERE chamado_lecom = ?", (chamado_lecom,))
                connection.commit()
                connection.close()
                sg.popup("Chamado excluído com sucesso!")
        else:
            sg.popup_error("Nenhuma linha selecionada para exclusão!")


# Funções para atualizar as tabelas
def atualizar_tabela_equipamentos():
    connection = sqlite3.connect("lecompy_data.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM equipamentos")
    equipamentos = cursor.fetchall()
    connection.close()
    return equipamentos

def atualizar_tabela_chamados():
    connection = sqlite3.connect("lecompy_data.db")
    cursor = connection.cursor()
    cursor.execute("""
    SELECT r.chamado_lecom, e.ativo, e.mac, e.numero_serie, e.fsan, r.data_inicio, r.data_conclusao, r.status, r.responsavel, r.modificado_por
    FROM registros r
    JOIN equipamentos e ON r.id_equipamento = e.id_equipamento
    """)
    chamados = cursor.fetchall()
    connection.close()
    return chamados

# Função principal para iniciar o programa
def main():
    login_screen()

# Iniciar o programa
if __name__ == "__main__":
    main()
