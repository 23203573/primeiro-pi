import mysql.connector
from mysql.connector import Error

def conectar():
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='104367',  # ajuste conforme seu ambiente
            database='lalumareDB'
        )
    except Error as e:
        print(f"Erro de conexão: {e}")
        return None

def inserir_cliente(nome, telefone, endereco, cpf="000.000.000-00"):
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        sql = "INSERT INTO cliente (cpf, nome, telefone, endereco) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (cpf, nome, telefone, endereco))
        conn.commit()
        id_cliente = cursor.lastrowid
        cursor.close()
        conn.close()
        return id_cliente

def inserir_pedido(cliente_id, funcionario_id, numero, valor, status,
                   forma_pagamento, forma_retirada, qtd_total):
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        sql = """
        INSERT INTO pedido (
            cliente_id, funcionario_id, numero, valor, status,
            forma_pagamento, forma_retirada, data_hora_pedido,
            data_hora_previsao, soma_qtd_produto
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s)
        """
        cursor.execute(sql, (
            cliente_id, funcionario_id, numero, valor, status,
            forma_pagamento, forma_retirada, qtd_total
        ))
        conn.commit()
        id_pedido = cursor.lastrowid
        cursor.close()
        conn.close()
        return id_pedido

def inserir_produtos(pedido_id, lista_produtos):
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        sql = """
        INSERT INTO produto (pedido_id, tipo_produto, qtd_produto, valor_produto, un_medida_produto)
        VALUES (%s, %s, %s, %s, %s)
        """
        for tipo, qtd, valor, unidade in lista_produtos:
            cursor.execute(sql, (pedido_id, tipo, qtd, valor, unidade))
        conn.commit()
        cursor.close()
        conn.close()
