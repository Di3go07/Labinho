''' Responsável pela criação das rotas de URL na aplicação '''

from flask import render_template, flash, session
from flask import request, redirect, url_for, render_template
from flask_login import login_required, login_user
from app import app
from app import db
from app import alquimias 
from app.models.models import Cardapio, Carrinho
from sqlalchemy import func

### ROTA PARA INDEX
@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:  # Verifica se o usuário está logado
        username = session['username']
        cargo = alquimias.resgatar_cargo(username)  # Obtém o cargo do usuário
        user = {'username': username, 'cargo': cargo}  # Passa o cargo para o template
    else:
        user = None
        cargo = 'cliente'

    return render_template(
        'index.html', 
        title='Home', 
        user=user,
        cargo = cargo
    )

### ROTA PARA LOGIN 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session: #realiza logout caso tenha algum usuário na sessão
        session.pop('username', None)  
        session.pop('cargo', None)
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password'].lower()

        if not alquimias.user_exists(username):
            flash('Usuário não encontrado')
            return redirect(url_for('login'))
        
        elif alquimias.validate_user_password(username, password):
            flash("Login bem-sucedido!")
            session['username'] = username
            session['cargo'] = alquimias.resgatar_cargo(username)  # Guarda o cargo na sessão

            return redirect(url_for('index'))  # Removido username=username, pois já está na sessão
        
        else:
            flash("Usuário ou senha inválidos")
            return redirect(url_for('login'))
    
    return render_template('login.html', title="Login")

### ROTA PARA REGISTRAR
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password'].lower()
        password2 = request.form['password2'].lower()

        if alquimias.user_exists(username):
            flash("Usuário já existe!")
            return redirect(url_for('login'))
        elif password != password2:
            flash("Senhas estão diferentes")
            return redirect(url_for('registro'))
        else:
            username = username
            email = request.form['email'].lower()
            password = request.form['password'].lower()

            alquimias.create_user(username, password, email)
            return redirect(url_for(f"login", username=username ))
        
    else:
        return render_template('registro.html', title=registro)

    
### ROTA PARA CARDAPIO
@app.route('/cardapio')
def cardapio():
    if 'username' in session:  # Verifica se o usuário está logado
        username = session['username']
        cargo = alquimias.resgatar_cargo(username)  # Obtém o cargo do usuário
        user = {'username': username, 'cargo': cargo}  # Passa o cargo para o template
    else:
        user = None
        cargo = 'cliente'

    individuais = Cardapio.query.filter_by(tipo="Individual").limit(4).all()
    porcoes = Cardapio.query.filter_by(tipo="Porção").limit(4).all()
    bebidas = Cardapio.query.filter_by(tipo="Bebida").limit(4).all()


    return render_template('cardapio.html', title='Cardapio', individuais=individuais, porcoes=porcoes, bebidas=bebidas, user=user)

### ROTA PARA UM TIPO NO CARDAPIO
@app.route('/cardapio/<tipo>')
def cardapioCompleto(tipo):
    if 'username' in session:  # Verifica se o usuário está logado
        username = session['username']
        cargo = alquimias.resgatar_cargo(username)  # Obtém o cargo do usuário
        user = {'username': username, 'cargo': cargo}  # Passa o cargo para o template
    else:
        user = None
        cargo = 'cliente'

    cardapio = Cardapio.query.filter_by(tipo=tipo).all()

    return render_template('cardapio_completo.html',  title=tipo, user=user, cardapio=cardapio)

### ROTA PARA REGISTRAR CARDAPIO
@app.route('/cadastro/cardapio', methods=['GET', 'POST'])
def registroCardapio():   
    if 'username' not in session:
            user = None
            return redirect(url_for('index'))

    if 'username' in session:
        username = session['username']
        cargo = alquimias.resgatar_cargo(username)
        user = {'username': username, 'cargo': cargo}

        if user['cargo'].lower() != 'gerente' and  user['cargo'].lower() != 'funcionário':
            return redirect(url_for('index'))

    if request.method == 'POST':
        valido, mensagem = alquimias.valida_prato(request.form)
        
        if valido:
            nome = request.form['nome'].capitalize()
            tipo = request.form['tipo'].capitalize() 
            valor = request.form['valor'].capitalize() 
            descricao = request.form['descricao'].capitalize() 
            imagem = request.form['imagem'].capitalize()

            alquimias.create_prato(nome, tipo, valor, descricao, imagem)
            flash(f'Prato registrado com sucesso!')
            return redirect(url_for('cardapio'))
        else:
            flash(mensagem)

    return render_template('registrar_prato.html', title='Registro', user=user)

### ROTA PARA ALTERAR CARGO
@app.route('/cadastro/user', methods=['GET', 'POST'])
def alterarCargo():  
    if 'username' not in session:
            user = None
            return redirect(url_for('index'))

    if 'username' in session:
        username = session['username']
        cargo = alquimias.resgatar_cargo(username)
        user = {'username': username, 'cargo': cargo}

        if user['cargo'].lower() != 'gerente' and  user['cargo'].lower() != 'funcionario':
            return redirect(url_for('index'))

    if request.method == 'POST':
        adm = session['username']
        usuario = request.form['nome'].lower()
        novo_cargo = request.form['cargo']
        senha_adm = request.form['senha'].lower()

        if not all([adm, usuario, novo_cargo, senha_adm]):
            flash('Todos os campos são obrigatórios.')
            return redirect(url_for('alterarCargo'))

        resultado = alquimias.validar_adm_password(adm, senha_adm)

        if resultado:
            valido, mensagem = alquimias.atualiza_cargo(usuario, novo_cargo)

            if valido:
                flash(mensagem)
                return redirect(url_for('index'))
            else:
                flash(mensagem)
                return redirect(url_for('alterarCargo'))
        else:
            flash(f'senha inválida para {adm}')
            return redirect(url_for('alterarCargo'))

    return render_template('mudar_cargo.html', title='Atualização', user=user)

### ROTA PARA EXCLUIR DO CARDAPIO
@app.route('/excluir_prato/<int:id>', methods=['POST'])
def excluirPrato(id):
    if 'username' not in session:
            user = None
            return redirect(url_for('index'))

    if 'username' in session:
        username = session['username']
        cargo = alquimias.resgatar_cargo(username)
        user = {'username': username, 'cargo': cargo}

        if user['cargo'].lower() != 'gerente' and  user['cargo'].lower() != 'funcionario':
            return redirect(url_for('index'))
        
    valido, mensagem = alquimias.excluir_prato(id)

    if valido:
        flash(mensagem)
        return redirect(url_for('index'))
    else:
        flash(mensagem)
        return redirect(url_for('cardapio'))

### ROTA PARA EDITAR PRODUTO
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editarPrato(id):
    # Verifica se o usuário está logado na sessão
    if 'username' not in session:
        return redirect(url_for('index'))  # Se não estiver, redireciona para a página principal

    username = session['username']
    cargo = alquimias.resgatar_cargo(username)
    user = {'username': username, 'cargo': cargo}

    # Verifica se o usuário tem permissão (cargo 'gerente' ou 'funcionario')
    if user['cargo'].lower() not in ['gerente', 'funcionario']:
        return redirect(url_for('index'))  # Redireciona se o usuário não tiver permissão

    if request.method == 'POST':
        senha_adm = request.form.get('senha')  
        nome = request.form.get('nome', '').strip().capitalize()  
        tipo = request.form.get('tipo', '').strip().capitalize()
        valor = request.form.get('valor', '').strip()  
        descricao = request.form.get('descricao', '').strip().capitalize()
        imagem = request.form.get('imagem', '').strip().capitalize()

        # Valida se os campos obrigatórios estão presentes
        if not nome or not tipo or not valor or not descricao or not imagem or not senha_adm:
            flash('Todos os campos devem ser preenchidos!', 'error')
            return redirect(url_for('editarPrato', id=id))

        # Valida a senha do administrador
        adm = session['username']
        resultado = alquimias.validar_adm_password(adm, senha_adm.lower())

        if resultado:
            # Se a senha for válida, tenta editar o prato
            try:
                valor = float(valor)  # Tenta converter o valor para float
            except ValueError:
                flash('Valor inválido!', 'error')
                return redirect(url_for('editarPrato', id=id))

            # Chama a função para editar o prato no banco de dados
            query = alquimias.editar_prato(id, nome, tipo, valor, descricao, imagem)
            if query:
                flash(f'Prato "{nome}" editado com sucesso!')
                return redirect(url_for('cardapio'))
            else:
                flash('Falha ao editar prato no banco de dados', 'error')
                return redirect(url_for('cardapio'))
        else:
            flash('Senha de administrador incorreta', 'error')
            return redirect(url_for('cardapio'))

    # Resgata as informações atuais do prato
    res = alquimias.info_pratos(id)

    if res:
        # Se o prato for encontrado, renderiza a página de edição com os dados atuais
        return render_template('editar_prato.html', 
                               title='Editar', 
                               nome=res[0], 
                               descricao=res[1], 
                               tipo=res[2], 
                               valor=res[3], 
                               imagem=res[4], 
                               user=user)
    else:
        flash('Prato não encontrado', 'error')
        return redirect(url_for('index'))  # Se o prato não for encontrado, redireciona para o index

### ROTA PARA RENDERIZAR CARRINHO
@app.route('/carrinho', methods=['GET', 'POST'])
def carrinho():
    if 'username' in session:  # Verifica se o usuário está logado
        username = session['username']
        cargo = alquimias.resgatar_cargo(username)
        user = {'username': username, 'cargo': cargo}
    else:
        return redirect(url_for('login'))

    id_user = alquimias.resgatar_id(username)

    #JOIN para buscar as informações do produto no carrinho
    carrinho = db.session.query(Carrinho, Cardapio.descricao, Cardapio.nome, Cardapio.imagem) \
        .join(Cardapio, Carrinho.produto_id == Cardapio.id) \
        .filter(Carrinho.user_id == id_user) \
        .all()

    # Consulta para obter o valor total somado de todos os itens no carrinho
    total = db.session.query(func.sum(Carrinho.quantidade * Cardapio.valor)) \
        .join(Cardapio, Carrinho.produto_id == Cardapio.id) \
        .filter(Carrinho.user_id == id_user) \
        .scalar()

    if total is None:
        total = 0

    return render_template(
        'carrinho.html', 
        title='Home', 
        user=user,
        carrinho=carrinho,
        total=total
    )

### ROTA PARA ADICIONAR AO CARRINHO
@app.route('/adicionar/<int:id>', methods=['POST'])
def adicionarPrato(id):
    if 'username' not in session:
        user = None
        return redirect(url_for('login'))
    
    usuario = session['username']
    id_user = alquimias.resgatar_id(usuario)

    valido, mensagem = alquimias.adicionar_carrinho(id_user, id, quantidade=1)
    
    if valido:
        flash(mensagem)
        return redirect(url_for('carrinho'))
    else:
        flash(mensagem)
        return redirect(url_for('cardapio'))

### ROTA PARA EXCLUIR DO CARRINHO
@app.route('/excluir_pedido/<int:id>', methods=['POST'])
def excluirPedido(id):
    if 'username' not in session:
            user = None
            return redirect(url_for('index'))
        
    valido, mensagem = alquimias.excluir_pedido(id)

    if valido:
        flash(mensagem)
        return redirect(url_for('index'))
    else:
        flash(mensagem)
        return redirect(url_for('carrinho'))

### ROTA PARA ALTERAR A QUANTIDADE
@app.route('/aumentar/<int:id>', methods=['POST'])
def adicionar(id):
    if 'username' not in session:
            user = None
            return redirect(url_for('index'))
    
    validar = alquimias.adicionar(id)

    if validar:
        return redirect(url_for('carrinho'))
    else:
        flash('Erro ao adicionar')
        return redirect(url_for('carrinho'))
@app.route('/reduzir/<int:id>', methods=['POST'])
def retirar(id):
    if 'username' not in session:
            user = None
            return redirect(url_for('index'))
    
    validar = alquimias.retirar(id)

    if validar:
        return redirect(url_for('carrinho'))
    else:
        flash('Limite atingido')
        return redirect(url_for('carrinho'))



