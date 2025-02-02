'''Arquivo com querys do banco de dados'''

from datetime import datetime
from sqlalchemy import select
from app import db
from app.models.models import User, Cardapio, Carrinho

def validate_user_password(username , password):
    '''Testa se o usuário e senha correspondem a um registro no banco'''
    res = db.session.scalars(select(User).where(User.username == username))
    res = res.first()

    return res and res.password == password

def validar_adm_password(adm, password):
    res = db.session.scalars(select(User).where(User.username == adm))
    res = res.first()

    return res.password == password

def user_exists(username):
    '''Testa se o usuário informado corresponde a um registro no banco'''
    res = db.session.scalars(select(User).where(User.username == username))

    return res.first()

def create_user(username, password, email, cargo='Cliente', remember=False):
    '''Cria um novo registro no banco'''
    new_user = User(
    username = username,
    password = password,
    email = email,
    cargo = cargo,
    remember = remember
    )
    db.session.add(new_user)
    db.session.commit()

def resgatar_id(username):
    res = db.session.scalars(select(User).where(User.username == username))
    res = res.first()
    
    return res.id

def resgatar_cargo(username):
    res = db.session.scalars(select(User).where(User.username == username))
    res = res.first()
    
    return res.cargo

def atualiza_cargo(username, cargo):
    res = db.session.scalars(select(User).where(User.username == username))
    res = res.first()

    if cargo.lower() in ["cliente", "funcionário", "gerente"]:
        res.cargo = cargo.capitalize()
        db.session.commit()
        
        return True, f'{username} agora é um {cargo.capitalize()}'
    else:
        return False, 'Escolha entre cliente, funcionário ou gerente'



def valida_prato(form):
    campos_obrigatorios = ['nome', 'tipo', 'valor', 'descricao', 'imagem']
    tipos_validos = ["Porção", "Individual", "Bebida"]

    # Verifica se todos os campos obrigatórios estão preenchidos
    for campo in campos_obrigatorios:
        if campo not in form or not form[campo].strip():
            return False, f'O campo {campo} é obrigatório.'

    # Verifica se o tipo é válido
    if form['tipo'].capitalize() not in tipos_validos:
        return False, 'Tipo inválido. Os tipos válidos são: Porção, Individual, Bebida.'

    # Verifica se o valor é um número positivo
    try:
        valor = float(form['valor'])
        if valor < 0:
            return False, 'O campo "valor" deve ser um número positivo.'
    except ValueError:
        return False, 'O campo "valor" deve ser um número válido.'

    # Verifica se o prato já existe no banco de dados
    prato_existente = db.session.scalars(select(Cardapio).where(Cardapio.nome == form['nome'].capitalize())).first()
    if prato_existente:
        return False, 'Comida já foi adicionada.'

    return True, ''

def create_prato(nome, tipo, valor, descricao, imagem):
    new_prato = Cardapio(
        nome=nome,
        tipo=tipo,
        valor=valor,
        descricao=descricao,
        imagem=imagem
    )

    db.session.add(new_prato)
    db.session.commit()

#resgata informações dos pratos
def info_pratos(id):
    prato = db.session.scalars(select(Cardapio).where(Cardapio.id == id)).first()
    if prato:
        return [prato.nome, prato.descricao, prato.tipo, prato.valor, prato.imagem]
    else:
        return False

#excluir prato
def excluir_prato(id):
    try:
        prato = db.session.scalars(select(Cardapio).where(Cardapio.id == id)).first()
        db.session.delete(prato)
        db.session.commit()

        return True, 'Produto removido'
    except:
        return False, 'Falha ao remover produto'
    
#edita prato
def editar_prato(id, nome, tipo, valor, descricao, imagem):
    try:
        prato = db.session.scalars(select(Cardapio).where(Cardapio.id == id)).first()
        if prato:
            prato.nome = nome
            prato.descricao = descricao
            prato.tipo = tipo
            prato.valor = valor
            prato.imagem = imagem

            db.session.commit()
            return True
        else:
            return False
    except:
        return False

#adicionar à tabela carrinho
def adicionar_carrinho(userId, produtoId, quantidade):
    try:
        produto = db.session.scalars(select(Cardapio).where(Cardapio.id == produtoId)).first()
        valor_total = produto.valor * quantidade

        # Verifica se o produto já existe no carrinho do usuário
        item_existente = db.session.scalars(select(Carrinho).where(Carrinho.user_id==userId, Carrinho.produto_id==produtoId)).first()

        if item_existente:
            return False, 'Produto já está no carrinho'

        else:
            item_novo = Carrinho(user_id=userId, produto_id=produtoId, quantidade=quantidade, valor_total=valor_total)
            db.session.add(item_novo)
            db.session.commit()

        return True, 'Produto salvo no carrinho'
    except:
        return False, 'Falha ao salvar produto'
    
#excluir pedido do carrinho
def excluir_pedido(id):
    try:
        pedido = db.session.scalars(select(Carrinho).where(Carrinho.id == id)).first()
        if pedido:
            db.session.delete(pedido)
            db.session.commit()
        else:
            return False, 'Pedido não encontrado'
    
        return True, 'Produto removido'
    except:
        return False, 'Falha ao remover produto'  
    
#alterar a quantidade
def adicionar(id):
        pedido = db.session.scalars(select(Carrinho).where(Carrinho.id == id)).first()
        pedido.quantidade += 1

        valor_produto = db.session.query(Cardapio.valor) \
        .join(Carrinho, Carrinho.produto_id == Cardapio.id) \
        .filter(Carrinho.id == id) \
        .first()

        pedido.valor_total = pedido.quantidade * valor_produto[0]
        db.session.commit()

        return True
def retirar(id):
        pedido = db.session.scalars(select(Carrinho).where(Carrinho.id == id)).first()
        if pedido.quantidade <= 1:
            return False

        pedido.quantidade -= 1

        valor_produto = db.session.query(Cardapio.valor) \
        .join(Carrinho, Carrinho.produto_id == Cardapio.id) \
        .filter(Carrinho.id == id) \
        .first()

        pedido.valor_total = pedido.quantidade * valor_produto[0]
        db.session.commit()

        return True
