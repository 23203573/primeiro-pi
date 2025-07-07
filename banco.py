import mysql.connector
from datetime import datetime
import uuid

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Cris1358!",
        database="lalumaredb"
    )

def inserir_cliente(nome, telefone, endereco):
    try:
        conn = conectar()
        cursor = conn.cursor()
        sql = """
            INSERT INTO cliente (id_cliente, nome, telefone, endereco)
            VALUES (%s, %s, %s, %s)
        """
        guid = str(uuid.uuid4())
        cursor.execute(sql, (guid, nome, telefone, endereco))
        conn.commit()
        id_cliente = cursor.lastrowid
        cursor.close()
        conn.close()
    except Exception as e:
        raise e
    
    return guid

def inserir_funcionario(nome, login, senha, email):
    conn = conectar()
    cursor = conn.cursor()
    sql = """
        INSERT INTO funcionario (id_funcionario, nome, nm_login, senha, email)
        VALUES (%s, %s, %s, %s, %s)
    """
    guid = str(uuid.uuid4())
    cursor.execute(sql, (guid, nome, login, senha, email))
    conn.commit()
    id_funcionario = cursor.lastrowid
    cursor.close()
    conn.close()
    return guid

def inserir_pedido(cliente_id, funcionario_id, numero, valor, status, forma_pagamento, forma_retirada, data_hora_previsao, soma_qtd_produto, adicionais):
    conn = conectar()
    cursor = conn.cursor()
    sql = """
        INSERT INTO pedido (
            id_pedido, id_cliente, id_funcionario, numero, valor, status,
            forma_pagamento, forma_retirada, data_hora_pedido, data_hora_previsao, soma_qtd_produto, adicionais
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    guid = str(uuid.uuid4())
    agora = datetime.now()
    cursor.execute(sql, (
        guid, cliente_id, funcionario_id, numero, valor, status,
        forma_pagamento, forma_retirada, agora, data_hora_previsao, soma_qtd_produto, adicionais
    ))
    conn.commit()
    id_pedido = cursor.lastrowid
    cursor.close()
    conn.close()
    return guid

def inserir_produto(pedido_id, tipo_produto, qtd_produto, valor_produto, un_medida_produto):
    conn = conectar()
    cursor = conn.cursor()
    sql = """
        INSERT INTO produto (id_produto, id_pedido, tipo_produto, qtd_produto, valor_produto, un_medida_produto)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    guid = str(uuid.uuid4())
    cursor.execute(sql, (guid, pedido_id, tipo_produto, qtd_produto, valor_produto, un_medida_produto))
    conn.commit()
    id_produto = cursor.lastrowid
    cursor.close()
    conn.close()
    return guid 

def get_existing_cliente(nome, telefone):
    try:
        conn = conectar()
        cursor = conn.cursor()
        sql = "SELECT id_cliente FROM cliente WHERE nome = %s AND telefone = %s"
        cursor.execute(sql, (nome, telefone))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            return result[0]
        else:
            return None
    except Exception as e:
        raise e

def get_all_pedidos():
    try:
        conn = conectar()
        cursor = conn.cursor()
        sql = "SELECT valor, forma_pagamento, forma_retirada, data_hora_pedido from pedido"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()

        return result
    except Exception as e:
        raise e

def get_adicionais():
    try:
        conn = conectar()
        cursor = conn.cursor()
        sql = "SELECT tipo_produto FROM produto WHERE valor_produto = 0 AND qtd_produto > 0 ORDER BY tipo_produto;"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()

        return result
    except Exception as e:
        raise e
    
def get_extras():
    try:
        conn = conectar()
        cursor = conn.cursor()
        sql = "SELECT tipo_produto, valor_produto FROM produto WHERE valor_produto <> 0 AND tipo_produto NOT LIKE '%Açai%' AND qtd_produto > 0 ORDER BY tipo_produto;"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()

        return result
    except Exception as e:
        raise e
    
def get_id_produtos(list_produtos):
    try:
        conn = conectar()
        cursor = conn.cursor()
        placeholders = ', '.join(['%s'] * len(list_produtos))
        sql = f"SELECT id_produto FROM produto WHERE tipo_produto IN ({placeholders});"
        cursor.execute(sql, tuple(list_produtos))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    
    except Exception as e:
        raise e
    
def update_qtd_produto(id_produto):
    try:
        conn = conectar()
        cursor = conn.cursor()
        sql = "UPDATE produto SET qtd_produto = qtd_produto - qtd_pedido WHERE id_produto = %s;"
        cursor.execute(sql, (int(id_produto),))
        conn.commit()
        cursor.close()
        conn.close()
    
    except Exception as e:
        raise e
    
def get_last_10_pedidos():
    try:
        conn = conectar()
        cursor = conn.cursor()
        sql = "select a.nome, b.valor, b.data_hora_pedido, b.adicionais from cliente a inner join pedido b on a.id_cliente = b.id_cliente order by b.data_hora_pedido desc limit 10;"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
    
        return result
    except Exception as e:
        raise e
    
def get_produto_status():
    try:
        conn = conectar()
        cursor = conn.cursor()
        sql = "select tipo_produto, qtd_produto, valor_produto, un_medida_produto, qtd_pedido from produto;"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
    
        return result
    except Exception as e:
        raise e
    
def get_statistics_adicionais():
    try:
        conn = conectar()
        cursor = conn.cursor()
        sql = "select adicionais from pedido;"
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
    
        return result
    except Exception as e:
        raise e
    
def get_produto(id_produto):
    try:
        conn = conectar()
        cursor = conn.cursor()
        sql = "select tipo_produto from produto where id_produto = %s;"
        cursor.execute(sql, (int(id_produto),))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
    
        return result[0][0]
    except Exception as e:
        raise e