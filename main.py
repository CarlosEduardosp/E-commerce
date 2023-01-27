from flask import Flask, render_template, request, url_for, send_from_directory, jsonify, redirect, flash
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

# instancia flask
app = Flask(__name__)

# instancia banco de dados
db = SQLAlchemy()

# chave secreta para o banco de dados
app.secret_key = "b'\x92O7\x1a\x0e\x94\xb2\xff\x04\xdaD\x98)\xc79-'"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///delivery.db"

# init do banco de dados.
db.init_app(app)


class ImagemPerfil(db.Model):

    """ criando a classe/tabela Carrinho do bd. """

    id_imagem = db.Column(db.Integer, primary_key=True)
    nome_imagem = db.Column(db.String, unique=False, nullable=False)

    def __init__(self, id_imagem, nome_imagem):
        self.id_imagem = id_imagem
        self.nome_imagem = nome_imagem


class Carrinho(db.Model):

    """ criando a classe/tabela Carrinho do bd. """

    id_compra = db.Column(db.Integer, primary_key=True)
    id_produto = db.Column(db.String, unique=False, nullable=False)
    id_cliente = db.Column(db.String, unique=False, nullable=False)

    def __init__(self,id_produto, id_cliente):
        self.id_produto = id_produto
        self.id_cliente = id_cliente


class Cliente(db.Model):

    """ criando a classe/tabela Cliente do bd."""

    id_cliente = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=False, nullable=False)
    senha = db.Column(db.String, unique=False, nullable=False)
    pedidos = db.Column(db.String, unique=False, nullable=True)
    apelido = db.Column(db.String, unique=False, nullable=False)
    end = db.Column(db.String, unique=False, nullable=False)

    def __init__(self, email, senha, apelido, end):
        self.email = email
        self.senha = senha
        self.apelido = apelido
        self.end = end


class Produto(db.Model):

    """ criando a classe/tabela Produto do bd. """

    id_produto = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, unique=False, nullable=False)
    descricao = db.Column(db.String, unique=False, nullable=False)
    preco = db.Column(db.String, unique=False, nullable=False)
    imagem = db.Column(db.String, unique=False, nullable=False)

    def __init__(self, nome, descricao, preco, imagem ):
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.imagem = imagem


class Pedido(db.Model):

    """ criando a classe/tabela Pedido do bd. """

    id_pedido = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.String, unique=False, nullable=False)
    id_produto = db.Column(db.Integer, unique=False, nullable=False)
    data_pedido = db.Column(db.String, unique=False, nullable=False)
    numero_pedido = db.Column(db.Integer, unique=False, nullable=False)
    valor = db.Column(db.Float, unique=False, nullable=False)
    status = db.Column(db.String, unique=False, nullable=False)

    def __init__(self, id_cliente, id_produto, data_pedido, numero_pedido, valor, status):
        self.id_cliente = id_cliente
        self.id_produto = id_produto
        self.data_pedido = data_pedido
        self.numero_pedido = numero_pedido
        self.valor = valor
        self.status = status


def validador_apelido(apelido):
    result = int(1)
    clientes = db.session.execute(db.select(Cliente)).all()
    for i in clientes:
        """ Verificação se o apelido  já está em uso. 
        casa esteja result recebe = 0, caso contrário = 1."""

        if apelido == i[0].apelido:
            result = int(0)
            break
        else:
            result = int(1)

    return result


def validador_email(email):
    result = int(1)
    clientes = db.session.execute(db.select(Cliente)).all()
    for i in clientes:
        """ Verificação se o email já está em uso. 
        casa esteja result recebe = 0, caso contrário = 1."""

        if email == i[0].email:
            result = int(0)
            break
        else:
            result = int(1)

    return result


def carrinho_compras(id_cliente):

    """ atualiza o numero de produtos no carrinho do cliente e devolve aos templates devidos. """

    produtos = db.session.execute(db.select(Produto)).all()
    carrinho_compras = db.session.execute(db.select(Carrinho)).all()
    num = 0

    """ compara o id_cliente com o id_cliente na tabela Carrinho, para achar os produtos do cliente na tabela. depois 
    compara id_produto do carrinho com id_produto em Produto e soma a quantidade em uma variável num que será 
    retornada. """
    for i in produtos:
        for j in carrinho_compras:
            if id_cliente == j[0].id_cliente:
                x = int(i[0].id_produto)
                y = int(j[0].id_produto)
                if x == y:
                    num = num + 1
    return num


@app.route('/cadastrar_cliente', defaults={'id_cliente':'Efetue o Login!'}, methods=['GET', 'POST'])
@app.route('/cadastrar_cliente/<id_cliente>', methods=['GET', 'POST'])
def cadastrar_cliente(id_cliente):

    """ Rota para cadastrar cliente, com confirmação de senha """

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')
        apelido = request.form.get('apelido')
        endereco = request.form.get('endereco')
        check = request.form.get('checkbox')

        resultado_apelido = validador_apelido(apelido)
        resultado_email = validador_email(email)
        """ se as senhas estiverem divergentes, retornará uma mensagem através da biblioteca flash."""
        if senha == confirmar_senha:

            if resultado_apelido == 1 and resultado_email == 1:
                cliente = Cliente(email, senha, apelido, endereco)
                db.session.add(cliente)
                db.session.commit()
                return redirect(url_for('login', id_cliente=id_cliente, email=email, senha=senha))

            elif resultado_apelido == 0 and resultado_email == 1:
                mensagem = 'Apelido já existente, por favor digite novamente!!'
                flash(mensagem)

            elif resultado_apelido == 1 and resultado_email == 0:
                mensagem = 'Email já existente, por favor digite novamente!!'
                flash(mensagem)

            else:
                mensagem = 'Apelido e Email já esxistentes, por favor digite novamente'
                flash(mensagem)

        else:
            flash('Senhas não conferem!! digite novamente')

    return render_template('cadastrar_cliente.html', id_cliente=id_cliente)


@app.route('/cadastrar_produto', defaults={'id_cliente':'Efetue o Login!'}, methods=['GET', 'POST'])
@app.route('/cadastrar_produto/<id_cliente>', methods=['GET','POST'])
def cadastrar_produto(id_cliente):

    """ rota para cadastro de produtos, inserindo imediatamente no banco de dados. """

    if request.method == 'POST':
        nome_produto = request.form.get('nome')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco')
        #recebendo post do arquivo para upload
        imagem = request.files.get('upload')

        #adquirindo nome do arquivo do upload
        nome_imagem = imagem.filename

        #salvando arquivo na pasta static.
        diretorio = '.\static'
        imagem.save(os.path.join(diretorio, nome_imagem))

        produto = Produto(nome=nome_produto, descricao=descricao, preco=preco, imagem=nome_imagem)
        db.session.add(produto)
        db.session.commit()
        return redirect(url_for('cadastrar_produto', id_cliente=id_cliente))

    return render_template('cadastrar_produto.html', id_cliente=id_cliente)


@app.route('/', defaults={'id_cliente':'Efetue o Login!'}, methods=['GET', 'POST'])
@app.route('/home/<id_cliente>', methods=['GET', 'POST'])
def homepage(id_cliente ):

    """ Página inicial, busca todos os dados na tabela Produto e faz a  exibição na tela. """

    produtos = db.session.execute(db.select(Produto)).all()
    nome_imagem = db.session.execute(db.select(ImagemPerfil)).all()


    num = carrinho_compras(id_cliente)

    #retorna todos os nomes dos arquivos na pasta static.
    img = os.listdir('.\static')
    carrinho = len(img)

    return render_template('home.html', num=num, carrinho=carrinho, produtos=produtos, id_cliente=id_cliente, nome_imagem=nome_imagem)


@app.route('/login', defaults={'id_cliente':'Efetue o Login!'}, methods=['GET', 'POST'])
@app.route('/login/<id_cliente>', methods=['GET', 'POST'])
def login(id_cliente):

    """ Realiza o login comparando os dados inseridos, com os da tabela Cliente. """

    clientes = db.session.execute(db.select(Cliente)).all()

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        mensagem = 'Nenhum usuário encontrado'
        for cliente in clientes:
            if email == cliente[0].email and senha == cliente[0].senha:
                return redirect(url_for('homepage', id_cliente=cliente[0].apelido))
            else:
                mensagem = 'Usuário não encontrado ou senha incorreta!!'
        flash(mensagem)

    num = carrinho_compras(id_cliente)

    return render_template('login.html',num=num, id_cliente=id_cliente)



@app.route('/addcarrinho', defaults={'id_cliente':'Efetue o Login!'}, methods=['GET', 'POST'])
@app.route('/addcarrinho/<id_cliente>/<produto>', methods=['GET', 'POST'])
def addcarrinho(id_cliente, produto):

    """ Adiciona produtos a tabela carrinho de clientes, e retorna a mensagem do nome do item adicionado"""

    add_produto = Carrinho(produto, id_cliente)
    db.session.add(add_produto)
    db.session.commit()

    produtos = db.session.execute(db.select(Produto)).all()
    produto = int(produto)
    for i in produtos:
        x = int(i[0].id_produto)
        if produto == x:
            produtox = i[0].nome
            mensagem = f'{id_cliente.upper()}, O item {produtox.upper()} foi adicionado ao seu carrinho.'
            flash(mensagem)

    return redirect(url_for('homepage', id_cliente=id_cliente, produto=produto))


@app.route('/carrinho', defaults={'id_cliente': 'Efetue o Login!'}, methods=['GET', 'POST'])
@app.route('/carrinho/<id_cliente>', methods=['GET', 'POST'])
def carrinho(id_cliente):

    """ Mostra os itens na tela, adicionados a tabela Carrinho pelo cliente."""

    carrinho_antigo = db.session.execute(db.select(Carrinho)).all()
    produtos = db.session.execute(db.select(Produto)).all()

    carrinho = []
    for i in carrinho_antigo:
        for j in produtos:
            if id_cliente == i[0].id_cliente:
                i[0].id_produto = int(i[0].id_produto)
                j[0].id_produto = int(j[0].id_produto)

                if i[0].id_produto == j[0].id_produto:
                    carrinho.append(j)

    num = carrinho_compras(id_cliente)
    return render_template('carrinho.html', id_cliente=id_cliente, carrinho=carrinho, num=num)


@app.route('/deletar', defaults={'id_cliente': 'Efetue o Login!'}, methods=['GET', 'POST'])
@app.route('/deletar/<id_cliente>/<produto>/<operacao>', methods=['GET', 'POST'])
def deletar(id_cliente, produto, operacao):

    """ função para deletar, item do carrinho, cliente, produto. recebe por parâmetro a variável operacao e
     onde: 1: deletar Carrinho, 2: deletar Cliente, 3: deletar produto."""

    if operacao == '1':
        dados_para_deletar = Carrinho.query.filter_by(id_produto=produto).first()
        db.session.delete(dados_para_deletar)
        db.session.commit()
        return redirect(url_for('carrinho', id_cliente=id_cliente))

    elif operacao == '2':

        clientes = db.session.execute(db.select(Cliente)).all()
        for i in clientes:
            produto = int(produto)
            comparador = int(i[0].id_cliente)
            if produto == comparador:
                apelido = i[0].apelido
                usuario = i[0].apelido

                pedidos = db.session.execute(db.select(Pedido)).all()
                cont = 0
                for x in pedidos:
                    if apelido == x[0].id_cliente:
                        cont  += 1


                """ deletar todos os pedidos do cliente.
                
                for j in range(cont):
                    dados_para_deletar = Pedido.query.filter_by(id_cliente=apelido).first()
                    db.session.delete(dados_para_deletar)
                    db.session.commit()
                mensagem = "Pedidos excluídos com Sucesso."
                flash(mensagem)"""

        if usuario == 'ADM':
            mensagem = 'Impossível de excluir o ADMINISTRADOR'
            flash(mensagem)
            return redirect(url_for('clientes', id_cliente=id_cliente))


        else:
            dados_para_deletar = Cliente.query.filter_by(id_cliente=produto).first()
            db.session.delete(dados_para_deletar)
            db.session.commit()
            mensagem = "Cliente foi excluído com Sucesso."
            flash(mensagem)

            return redirect(url_for('clientes', id_cliente=id_cliente))

    elif operacao == '3':
        dados_para_deletar = Produto.query.filter_by(id_produto=produto).first()
        db.session.delete(dados_para_deletar)
        db.session.commit()
        return redirect(url_for('produtos', id_cliente=id_cliente))


    else:
        return redirect(url_for('carrinho', id_cliente=id_cliente))


@app.route('/sair/<id_cliente>', methods=['GET', 'POST'])
def sair(id_cliente):

    """ Função para encerrar o login. e o id_cliente passa a ser 'Efetue o login!'."""

    return redirect(url_for('homepage', id_cliente='Efetue o Login!'))


@app.route('/clientes/<id_cliente>', methods=['GET', 'POST'])
def clientes(id_cliente):

    """ Mostra na tela todos os clientes cadastrados. """

    lista_clientes = []
    clientes = db.session.execute(db.select(Cliente)).all()
    for i in clientes:
        lista_clientes.append(i[0])
    return render_template('clientes.html', id_cliente=id_cliente, lista_clientes=lista_clientes)


@app.route('/produtos/<id_cliente>', methods=['GET', 'POST'])
def produtos(id_cliente):

    """ mostra na tela todos os produtos cadastrados. """

    lista_produtos = []
    produtos = db.session.execute(db.select(Produto)).all()
    for i in produtos:
        lista_produtos.append(i[0])
    return render_template('produtos.html', id_cliente=id_cliente, lista_produtos=lista_produtos)


@app.route('/minhas_compras/<id_cliente>', methods=['GET', 'POST'])
def minhas_compras(id_cliente):

    """ Mostra todos os pedidos do cliente logado. """

    num = carrinho_compras(id_cliente)
    lista_pedidos = []
    produtos = db.session.execute(db.select(Produto)).all()
    pedidos = db.session.execute(db.select(Pedido)).all()
    for i in pedidos:
        lista_pedidos.append(i[0])
    return render_template('minhas_compras.html',num=num, id_cliente=id_cliente, lista_pedidos=lista_pedidos, produtos=produtos)


@app.route('/pedido/<id_cliente>', methods=['GET', 'POST'])
def pedido(id_cliente):

    """ Mostra os detalhes do pedido, como produtos e especificações, dados do cliente, e também os valores"""

    carrinho_antigo = db.session.execute(db.select(Carrinho)).all()
    produtos = db.session.execute(db.select(Produto)).all()
    cliente =  db.session.execute(db.select(Cliente)).all()

    carrinho = []

    """ colocando os dados dos produtos do carrinho em uma lista. """
    for i in carrinho_antigo:
        for j in produtos:
            if id_cliente == i[0].id_cliente:
                i[0].id_produto = int(i[0].id_produto)
                j[0].id_produto = int(j[0].id_produto)

                if i[0].id_produto == j[0].id_produto:
                    carrinho.append(j)

    num = carrinho_compras(id_cliente)

    """ colocando os dados co cliente em uma lista."""
    clientes = []
    for i in cliente:
        if id_cliente == i[0].apelido:
            clientes.append(i[0])
    """ somando os valores dos produtos."""
    valor = int(0)
    for i in carrinho:
        i[0].preco = int(i[0].preco)
        valor += i[0].preco

    return  render_template('pedido.html', id_cliente=id_cliente, carrinho=carrinho, num=num, clientes=clientes, valor=valor)


@app.route('/editar/<id_cliente>', methods=['GET', 'POST'])
def editar(id_cliente):

    #coletando o nome da antiga imagem no bd.
    if request.method == 'POST':
        arquivo = db.session.execute(db.select(ImagemPerfil)).all()
        nome_da_imagem_antiga = arquivo[0][0].nome_imagem

        # recebendo post do arquivo para upload
        imagem = request.files.get('upload')

        # adquirindo nome do arquivo do upload
        nome_imagem = imagem.filename

        if imagem:

            # removendo a imagem antiga do diretório.
            path = ".\static\imagem"
            dir = os.listdir(path)
            for i in dir:
                if nome_da_imagem_antiga == i:
                    os.remove('{}/{}'.format(path, nome_da_imagem_antiga))

            # salvando arquivo/imagem nova na pasta static.
            diretorio = '.\static\imagem'
            imagem.save(os.path.join(diretorio, nome_imagem))

            # deletando a imagem antiga do banco de dados.
            dados_para_deletar = ImagemPerfil.query.filter_by(id_imagem=1).first()
            db.session.delete(dados_para_deletar)
            db.session.commit()

            # salvando a nova imagem no bd.
            dados = ImagemPerfil(1, nome_imagem=nome_imagem)
            db.session.add(dados)
            db.session.commit()

            return redirect(url_for('homepage', id_cliente=id_cliente))

    return render_template('editar.html', id_cliente=id_cliente)


@app.route('/confirmar_pedido/<id_cliente>/<valor>', methods=['GET', 'POST'])
def confirmar_pedido(id_cliente, valor):

    """ Confirmação do pedido, com todos os dados na tela, Dados pessoais, dados do pedido, e dados dos produtos. """

    todos_os_produtos = db.session.execute(db.select(Produto)).all()
    pedidos = db.session.execute(db.select(Pedido)).all()
    carrinho = db.session.execute(db.select(Carrinho)).all()
    todos_os_cliente = db.session.execute(db.select(Cliente)).all()

    """ Dados do cliente"""
    cliente = []
    for i in todos_os_cliente:
        if i[0].apelido == id_cliente:
            cliente.append(i)

    """ Dados dos produtos """
    produto = []
    for i in carrinho:
        if id_cliente == i[0].id_cliente:
            produto.append(int(i[0].id_produto))

    #recebendo a data atual
    data_pedido = date.today().strftime('%d/%m/%Y')

    """ Somando o numero do pedido, para não sair um pedido com o mesmo numero que outro."""
    if pedidos:
        for i in pedidos:
            numero_pedido = i[0].numero_pedido + 1
    else:
        numero_pedido = 1

    status = 'Pedido Iniciado'

    """ Adicionando os pedidos na tabela do banco de dados, e removendo os dados da tabela Carrinho."""
    produtos = []
    if produto:
        for i in produto:
            id_produto = i
            dados = Pedido(id_cliente, id_produto, data_pedido, numero_pedido, valor, status)
            db.session.add(dados)
            db.session.commit()

            dados_para_deletar = Carrinho.query.filter_by(id_cliente=id_cliente).first()
            db.session.delete(dados_para_deletar)
            db.session.commit()

            dados_do_pedido = Pedido.query.filter_by(numero_pedido=numero_pedido).first()

            for j in todos_os_produtos:
                if j[0].id_produto == i:
                    produtos.append(j)

        return render_template('confirmacao.html', id_cliente=id_cliente, dados_do_pedido=dados_do_pedido, produtos=produtos, cliente=cliente)

    return render_template('pedido.html', id_cliente=id_cliente)


if __name__ == '__main__':
    app.run(debug=True)
    with app.app_context():
        db.create_all()

