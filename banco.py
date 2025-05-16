import mysql.connector
from datetime import datetime

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="104367",
        database="lalumareDB"
    )

def inserir_cliente(cpf, nome, telefone, endereco):
    conn = conectar()
    cursor = conn.cursor()
    sql = """
        INSERT INTO cliente (cpf, nome, telefone, endereco)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (cpf, nome, telefone, endereco))
    conn.commit()
    id_cliente = cursor.lastrowid
    cursor.close()
    conn.close()
    return id_cliente

def inserir_funcionario(cpf, nome, login, senha, email):
    conn = conectar()
    cursor = conn.cursor()
    sql = """
        INSERT INTO funcionario (cpf, nome, nm_login, senha, email)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (cpf, nome, login, senha, email))
    conn.commit()
    id_funcionario = cursor.lastrowid
    cursor.close()
    conn.close()
    return id_funcionario

def inserir_pedido(cliente_id, funcionario_id, numero, valor, status, forma_pagamento, forma_retirada, data_hora_previsao, soma_qtd_produto):
    conn = conectar()
    cursor = conn.cursor()
    sql = """
        INSERT INTO pedido (
            cliente_id, funcionario_id, numero, valor, status,
            forma_pagamento, forma_retirada, data_hora_pedido, data_hora_previsao, soma_qtd_produto
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    agora = datetime.now()
    cursor.execute(sql, (
        cliente_id, funcionario_id, numero, valor, status,
        forma_pagamento, forma_retirada, agora, data_hora_previsao, soma_qtd_produto
    ))
    conn.commit()
    id_pedido = cursor.lastrowid
    cursor.close()
    conn.close()
    return id_pedido

def inserir_produto(pedido_id, tipo_produto, qtd_produto, valor_produto, un_medida_produto):
    conn = conectar()
    cursor = conn.cursor()
    sql = """
        INSERT INTO produto (pedido_id, tipo_produto, qtd_produto, valor_produto, un_medida_produto)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (pedido_id, tipo_produto, qtd_produto, valor_produto, un_medida_produto))
    conn.commit()
    id_produto = cursor.lastrowid
    cursor.close()
    conn.close()
    return id_produto
