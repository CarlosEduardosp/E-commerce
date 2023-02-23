from flask import Flask, render_template, request, url_for, send_from_directory, jsonify, redirect, flash
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import requests
import random
import time
import smtplib
import email.message


# instancia flask
app = Flask(__name__)

# instancia banco de dados
db: SQLAlchemy = SQLAlchemy()

# chave secreta para o banco de dados
app.secret_key = "b'\x92O7\x1a\x0e\x94\xb2\xff\x04\xdaD\x98)\xc79-'"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///delivery.db"

# init do banco de dados.
db.init_app(app)

dados_cadastro_clientes = []
endereco = []


class Codigo(db.Model):
    id_codigo = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String, unique=False, nullable=False)

    def __init__(self, codigo):
        self.codigo = codigo


class Cor(db.Model):
    id_cor = db.Column(db.Integer, primary_key=True)
    cor = db.Column(db.String, unique=False, nullable=False)

    def __init__(self, cor):
        self.cor = cor


class Endereco(db.Model):
    """ criando tabela endereco_cliente """

    id_endereco = db.Column(db.Integer, primary_key=True)
    cep_cliente = db.Column(db.String, unique=False, nullable=False)
    estado = db.Column(db.String, unique=False, nullable=False)
    cidade = db.Column(db.String, unique=False, nullable=False)
    bairro = db.Column(db.String, unique=False, nullable=False)
    logradouro = db.Column(db.String, unique=False, nullable=False)
    complemento = db.Column(db.String, unique=False, nullable=False)
    id_cliente = db.Column(db.String, unique=False, nullable=False)

    def __init__(self, cep_cliente, estado, cidade, bairro, logradouro, complemento, id_cliente):
        self.cep_cliente = cep_cliente
        self.estado = estado
        self.cidade = cidade
        self.bairro = bairro
        self.logradouro = logradouro
        self.complemento = complemento
        self.id_cliente = id_cliente


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

    def __init__(self, id_produto, id_cliente):
        self.id_produto = id_produto
        self.id_cliente = id_cliente


class Cliente(db.Model):
    """ criando a classe/tabela Cliente do bd."""

    id_cliente = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=False, nullable=False)
    senha = db.Column(db.String, unique=False, nullable=False)
    apelido = db.Column(db.String, unique=False, nullable=False)
    cep_cliente = db.Column(db.String, unique=False, nullable=False)

    def __init__(self, email, senha, apelido, cep_cliente):
        self.email = email
        self.senha = senha
        self.apelido = apelido
        self.cep_cliente = cep_cliente


class Produto(db.Model):
    """ criando a classe/tabela Produto do bd. """

    id_produto = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, unique=False, nullable=False)
    descricao = db.Column(db.String, unique=False, nullable=False)
    preco = db.Column(db.String, unique=False, nullable=False)
    imagem = db.Column(db.String, unique=False, nullable=False)

    def __init__(self, nome, descricao, preco, imagem):
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


def enviar_email_codigo(codigo, email_destinatario):

    """
    envio de email com o codigo de validação, para cadastrar.
    """
    corpo_email = f"<p>Seu código para validação é: {codigo}</p>"

    msg = email.message.Message()
    msg['Subject'] = "<h2>Validação de Email.</h2>"
    msg['From'] = f"tec.mundo.py@gmail.com"
    msg['To'] = f'{email_destinatario}'
    password = f'jakhonuthvdvrkvw'
    msg.add_header('Content-Type', 'text/html' )
    msg.set_payload(corpo_email)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()

    s.login(msg['From'], password)
    s.sendmail(msg["from"], [msg["to"]], msg.as_string().encode("utf-8"))


def enviar_email_cadastro(nome, email_destinatario):

    """ envio de email de boas vindas. após o cadastro """
    corpo_email = f"<p>Olá {nome},</p>" \
                  f"<p>Seja Muito Bem Vindo!!</P> " \
                  f"<p>Seu perfil foi aceito com sucesso.</p>"\
                  f"<p>Esperamos que tenha uma experiência agradável, " \
                  f"e para o que precisar conte conosco.</p>"

    msg = email.message.Message()
    msg['Subject'] = "<h2>Cadastro Finalizado com Sucesso!</h2>"
    msg['From'] = f"tec.mundo.py@gmail.com"
    msg['To'] = f'{email_destinatario}'
    password = f'jakhonuthvdvrkvw'
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()

    s.login(msg['From'], password)
    s.sendmail(msg["from"], [msg["to"]], msg.as_string().encode("utf-8"))


def enviar_email_confirmaPedido(nome, email_destinatario, dados_do_pedido, todos_os_produtos):

    """ envio de email de confirmação de pedido """

    corpo_email = f"<p class='text-center'>Olá {nome},</p>" \
                  f"<p>Seu Pedido Foi Efetuado Com Sucesso.</P> " \
                  f"<p>Confira abaixo os dados do seu pedido:</p>"\
                  f"<p>Nº Pedido: {dados_do_pedido.numero_pedido}</p>"\
                  f"<p>Valor: R$ {dados_do_pedido.valor},00 </p>"\
                  f"<p>Data do Pedido: {dados_do_pedido.data_pedido}</p>" \
                  f"<p>Status do Pedido: {dados_do_pedido.status}</p>" \
                  f"<p>Estamos trabalhando para que seu pedido chegue o mais rápido possível.</p>"\
                  f"<p>Fique atento ao seu Email, pois, a cada atualização do seu pedido " \
                  f"mandaremos uma mensagem por aqui.</p>"\
                  f"<p>Obrigado Por Comprar conosco.</p>"

    msg = email.message.Message()
    msg['Subject'] = "Pedido Efetuado com Sucesso!".upper()
    msg['From'] = f"tec.mundo.py@gmail.com"
    msg['To'] = f'{email_destinatario}'
    password = f'jakhonuthvdvrkvw'
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()

    s.login(msg['From'], password)
    s.sendmail(msg["from"], [msg["to"]], msg.as_string().encode("utf-8"))


def enviar_email_status(status, pedido, nome, email_destinatario):

    if status == 'Saiu p/ Entrega':

        """ envio de email de status do pedido """
        corpo_email = f"<p>Olá {nome},</p>" \
                      f"<p>Seu pedido nº {pedido}, já {status}. </P> " \
                      f"<p>E em breve chegará em seu endereço cadastrado em nosso sistema.</p>"\
                      f"<p>Fique atento !!</p>"
        msg = email.message.Message()
        msg['Subject'] = f"Seu Pedido {status} !!".upper()
        msg['From'] = f"tec.mundo.py@gmail.com"
        msg['To'] = f'{email_destinatario}'
        password = f'jakhonuthvdvrkvw'
        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(corpo_email)

        s = smtplib.SMTP('smtp.gmail.com: 587')
        s.starttls()

        s.login(msg['From'], password)
        s.sendmail(msg["from"], [msg["to"]], msg.as_string().encode("utf-8"))

    elif status == 'Finalizado':

        """ envio de email de status do pedido """
        corpo_email = f"<p>Olá {nome},</p>" \
                      f"<p>Seu pedido nº {pedido}, Foi recebido e, sendo assim, modificamos o seu status para: {status}. </P> " \
                      f"<p>Agradecemos sua compra e esperamos te ver por aqui outra vez!!.</p>"\

        msg = email.message.Message()
        msg['Subject'] = f"Seu Pedido foi {status} !!".upper()
        msg['From'] = f"tec.mundo.py@gmail.com"
        msg['To'] = f'{email_destinatario}'
        password = f'jakhonuthvdvrkvw'
        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(corpo_email)

        s = smtplib.SMTP('smtp.gmail.com: 587')
        s.starttls()

        s.login(msg['From'], password)
        s.sendmail(msg["from"], [msg["to"]], msg.as_string().encode("utf-8"))

    elif status == 'Cancelado':

        """ envio de email de status do pedido """
        corpo_email = f"<p>Olá {nome},</p>" \
                      f"<p>Seu pedido nº {pedido}, foi {status}. </P> " \
                      f"<p>qualquer dúvida sobre o que possa ter ocorrido, entre em contato conosco.</p>"\
                      f"<p>Agradecemos sua atenção!!</p>"

        msg = email.message.Message()
        msg['Subject'] = f"Seu Pedido foi {status} !!".upper()
        msg['From'] = f"tec.mundo.py@gmail.com"
        msg['To'] = f'{email_destinatario}'
        password = f'jakhonuthvdvrkvw'
        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(corpo_email)

        s = smtplib.SMTP('smtp.gmail.com: 587')
        s.starttls()

        s.login(msg['From'], password)
        s.sendmail(msg["from"], [msg["to"]], msg.as_string().encode("utf-8"))


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


def pesquisar_cep(cep_cliente):
    """Busca o endereço do usuário através do seu cep. com a Api do viacep."""

    cep_cliente = cep_cliente.replace("-", "").replace(".", "").replace(" ", "")

    if len(cep_cliente) == 8:
        link = f'https://viacep.com.br/ws/{cep_cliente}/json/'

        requisicao = requests.get(link)

        dic_requisicao = requisicao.json()

        if 'erro' not in dic_requisicao:
            logradouro = dic_requisicao['logradouro']
            complemento = dic_requisicao['complemento']
            if not complemento:
                complemento = 'Complemente aqui...'
            uf = dic_requisicao['uf']
            cidade = dic_requisicao['localidade']
            bairro = dic_requisicao['bairro']

            endereco = [uf, cidade, bairro, logradouro, complemento]
            return endereco
        else:
            flash('Cep Inválido !! Tente outra vez.')
            return None
    else:
        flash('Cep Inválido !! Tente outra vez.')
        return None


@app.route('/cadastrar_cliente', defaults={'id_cliente': 'Efetue o Login!'}, methods=['GET', 'POST'])
@app.route('/cadastrar_cliente/<id_cliente>', methods=['GET', 'POST'])
def cadastrar_cliente(id_cliente):
    global endereco
    endereco = ['---', '---', '---', '---', '---']

    """ Rota para cadastrar cliente, com confirmação de senha """

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')
        apelido = request.form.get('apelido')
        cep_cliente = request.form.get('end')
        complemento_form = request.form.get('complemento')

        """ salvando os dados do endereço pelo cep pesquisado."""

        endereco = pesquisar_cep(cep_cliente)

        if endereco != None:
            uf = endereco[0]
            cidade = endereco[1]
            bairro = endereco[2]
            logradouro = endereco[3]
            if complemento_form:
                endereco[4] = complemento_form

        """ verifica se existe endereço no cep, se senha não está vazia, ou se o complemento não está vazio. """

        if endereco != None and not senha or not complemento_form:
            return render_template('cadastrar_cliente.html', id_cliente=id_cliente, endereco=endereco, email=email,
                                   apelido=apelido, cep_cliente=cep_cliente, complemento_form=complemento_form)

        resultado_apelido = validador_apelido(apelido)
        resultado_email = validador_email(email)
        """ se as senhas estiverem divergentes, retornará uma mensagem através da biblioteca flash."""
        if senha == confirmar_senha:

            """ Montando o codigo que será enviado por email para verificação do mesmo"""
            if resultado_apelido == 1 and resultado_email == 1:
                codigo1 = random.randint(0, 9)
                codigo2 = random.randint(0, 9)
                codigo3 = random.randint(0, 9)
                codigo4 = random.randint(0, 9)
                codigo = str(codigo1) + str(codigo2) + str(codigo3) + str(codigo4)

                """enviando o email com codigo"""
                enviar_email_codigo(codigo=codigo, email_destinatario=email)

                """ deleta o codigo antigo do banco de dados"""
                dados_para_deletar = Codigo.query.filter_by(id_codigo=1).first()
                if dados_para_deletar:
                    db.session.delete(dados_para_deletar)
                    db.session.commit()

                """ Adicionando o codigo no banco de dados"""
                dados = Codigo(codigo)
                db.session.add(dados)
                db.session.commit()

                """ adicionando dados para cadastro na rota validar_email"""
                global dados_cadastro_clientes
                dados_cadastro_clientes = []
                dados_cadastro_clientes.append(email)
                dados_cadastro_clientes.append(senha)
                dados_cadastro_clientes.append(apelido)
                dados_cadastro_clientes.append(cep_cliente)

                return redirect(url_for('validar_email', id_cliente=id_cliente, email=email))

            elif resultado_apelido == 0 and resultado_email == 1:
                mensagem = 'Apelido já existente, por favor digite novamente!!'
                flash(mensagem)
                return render_template('cadastrar_cliente.html', id_cliente=id_cliente, endereco=endereco, email=email,
                                       apelido=apelido,
                                       cep_cliente=cep_cliente, complemento_form=complemento_form)

            elif resultado_apelido == 1 and resultado_email == 0:
                mensagem = 'Email já existente, por favor digite novamente!!'
                flash(mensagem)
                return render_template('cadastrar_cliente.html', id_cliente=id_cliente, endereco=endereco, email=email,
                                       apelido=apelido,
                                       cep_cliente=cep_cliente, complemento_form=complemento_form)

            else:
                mensagem = 'Apelido e Email já existentes, por favor digite novamente'
                flash(mensagem)
                return render_template('cadastrar_cliente.html', id_cliente=id_cliente, endereco=endereco, email=email,
                                       apelido=apelido,
                                       cep_cliente=cep_cliente, complemento_form=complemento_form)

        else:
            flash('Senhas não conferem!! digite novamente')
            return render_template('cadastrar_cliente.html', id_cliente=id_cliente, endereco=endereco, email=email,
                                   apelido=apelido,
                                   cep_cliente=cep_cliente, complemento_form=complemento_form)

    return render_template('cadastrar_cliente.html', id_cliente=id_cliente, endereco=endereco)


@app.route('/validar_email', defaults={'id_cliente': 'Efetue o Login!'}, methods=['GET', 'POST'])
@app.route('/validar_email/<id_cliente>', methods=['GET', 'POST'])
def validar_email(id_cliente):
    codigo = db.session.execute(db.select(Codigo)).all()
    codigo = codigo[0][0].codigo
    email = dados_cadastro_clientes[0]

    if request.method == 'POST':
        codigo_digitado = request.form.get('numero1')

        if codigo == codigo_digitado:
            email = dados_cadastro_clientes[0]
            senha = dados_cadastro_clientes[1]
            apelido = dados_cadastro_clientes[2]
            cep = dados_cadastro_clientes[3]

            dados_endereco = Endereco(cep, endereco[0], endereco[1], endereco[2], endereco[3], endereco[4], apelido)
            db.session.add(dados_endereco)
            db.session.commit()

            dados = Cliente(email, senha, apelido, cep)
            db.session.add(dados)
            db.session.commit()

            enviar_email_cadastro(nome=apelido,email_destinatario=email)

            return redirect(url_for('homepage', id_cliente=dados_cadastro_clientes[2]))
        else:
            flash('Código digitado não confere!!')

    return render_template('validacao_email.html', id_cliente=id_cliente, email=email)


@app.route('/cadastrar_produto', defaults={'id_cliente': 'Efetue o Login!'}, methods=['GET', 'POST'])
@app.route('/cadastrar_produto/<id_cliente>', methods=['GET', 'POST'])
def cadastrar_produto(id_cliente):
    """ rota para cadastro de produtos, inserindo imediatamente no banco de dados. """

    if request.method == 'POST':
        nome_produto = request.form.get('nome')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco')
        # recebendo post do arquivo para upload
        imagem = request.files.get('upload')

        # adquirindo nome do arquivo do upload
        nome_imagem = imagem.filename

        # salvando arquivo na pasta static.
        diretorio = './static'
        imagem.save(os.path.join(diretorio, nome_imagem))

        produto = Produto(nome=nome_produto, descricao=descricao, preco=preco, imagem=nome_imagem)
        db.session.add(produto)
        db.session.commit()
        return redirect(url_for('cadastrar_produto', id_cliente=id_cliente))

    return render_template('cadastrar_produto.html', id_cliente=id_cliente)


@app.route('/', defaults={'id_cliente': 'Efetue o Login!'}, methods=['GET', 'POST'])
@app.route('/home/<id_cliente>', methods=['GET', 'POST'])
def homepage(id_cliente):
    """ Página inicial, busca todos os dados na tabela Produto e faz a  exibição na tela. """

    produtos = db.session.execute(db.select(Produto)).all()
    nome_imagem = db.session.execute(db.select(ImagemPerfil)).all()

    num = carrinho_compras(id_cliente)

    # retorna todos os nomes dos arquivos na pasta static.
    path = "./static"
    img = os.listdir(path)

    # recupera a quantidade de imagens na pasta
    carrinho = len(img)

    return render_template('home.html', num=num, carrinho=carrinho, produtos=produtos, id_cliente=id_cliente,
                           nome_imagem=nome_imagem)


@app.route('/login', defaults={'id_cliente': 'Efetue o Login!'}, methods=['GET', 'POST'])
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

    return render_template('login.html', num=num, id_cliente=id_cliente)


@app.route('/addcarrinho', defaults={'id_cliente': 'Efetue o Login!'}, methods=['GET', 'POST'])
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
                        cont += 1

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

            dados_para_deletar = Endereco.query.filter_by(id_cliente=usuario).first()
            db.session.delete(dados_para_deletar)
            db.session.commit()

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
    endereco = db.session.execute(db.select(Endereco)).all()

    lista_clientes = []
    clientes = db.session.execute(db.select(Cliente)).all()
    for i in clientes:
        lista_clientes.append(i[0])
    return render_template('clientes.html', id_cliente=id_cliente, lista_clientes=lista_clientes, endereco=endereco)


@app.route('/produtos/<id_cliente>/<id_produto>', methods=['GET', 'POST'])
def produtos(id_cliente, id_produto):
    """ mostra na tela todos os produtos cadastrados. """

    if id_produto:
        id_produto = int(id_produto)
    else:
        id_produto = ''

    produtos = db.session.execute(db.select(Produto)).all()

    if request.method == 'POST':

        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco')
        for i in produtos:
            if i[0].id_produto == id_produto:
                Produto.query.filter_by(id_produto=id_produto).update(
                    {'nome': f"{nome}", 'descricao': f"{descricao}",
                     'preco': f"{preco}", "imagem": f"{i[0].imagem}"})
                db.session.commit()
                mensagem = f'Produto {nome}, Editado com Sucesso.'
                flash(mensagem)
                return redirect(url_for('produtos', id_cliente=id_cliente, id_produto=0))


    lista_produtos = []
    cont = []
    x = int(0)
    for i in produtos:
        lista_produtos.append(i[0])
        cont.append(x+1)
        x += 1
    quantidade = len(lista_produtos)
    return render_template('produtos.html',  id_cliente=id_cliente, lista_produtos=lista_produtos, cont=cont, quantidade=quantidade )


@app.route('/editar_produtos/<id_cliente>/<id_produto>', methods=['GET', 'POST'])
def editar_produtos(id_cliente, id_produto):

    if id_produto:
        id_produto = int(id_produto)
    else:
        id_produto = ''

    lista_produtos = []
    cont = []
    x = int(0)
    produtos = db.session.execute(db.select(Produto)).all()
    for i in produtos:
        lista_produtos.append(i[0])
        cont.append(x + 1)
        x += 1
    quantidade = len(lista_produtos)

    return render_template('editar_produtos.html', id_produto=id_produto, id_cliente=id_cliente, lista_produtos=lista_produtos, cont=cont, quantidade=quantidade )


@app.route('/minhas_compras/<id_cliente>', methods=['GET', 'POST'])
def minhas_compras(id_cliente):
    """ Mostra todos os pedidos do cliente logado. """

    num = carrinho_compras(id_cliente)

    pedidos = db.session.execute(db.select(Pedido)).all()
    produtos = db.session.execute(db.select(Produto)).all()
    clientes = db.session.execute(db.select(Cliente)).all()

    produtos_cliente = []
    lista_pedidos = []
    verificar = ''
    for pedido in pedidos:
        for cliente in clientes:
            if pedido[0].id_cliente == cliente[0].apelido:
                if verificar != pedido[0].numero_pedido:
                    dados_pedido = {"numero_pedido": pedido[0].numero_pedido, "valor": pedido[0].valor,
                                    "id_cliente": pedido[0].id_cliente,
                                    "cep": cliente[0].cep_cliente, "status": pedido[0].status,
                                    "id_pedido": pedido[0].id_pedido, "data_pedido": pedido[0].data_pedido}
                    lista_pedidos.insert(0, dados_pedido)
                for x in produtos:
                    if x[0].id_produto == pedido[0].id_produto:
                        produtos_cliente.append(x)
                    verificar = pedido[0].numero_pedido


    return render_template('minhas_compras.html', num=num, id_cliente=id_cliente, lista_pedidos=lista_pedidos,
                           produtos=produtos, pedidos=pedidos, produtos_cliente=produtos_cliente)


@app.route('/pedido/<id_cliente>', methods=['GET', 'POST'])
def pedido(id_cliente):
    """ Mostra os detalhes do pedido, como produtos e especificações, dados do cliente, e também os valores"""

    end = db.session.execute(db.select(Endereco)).all()
    carrinho_antigo = db.session.execute(db.select(Carrinho)).all()
    produtos = db.session.execute(db.select(Produto)).all()
    cliente = db.session.execute(db.select(Cliente)).all()
    if carrinho_antigo:

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

        return render_template('pedido.html', id_cliente=id_cliente, carrinho=carrinho, num=num, clientes=clientes,
                               valor=valor, end=end)

    flash('Não existe pedido para pagar!!')
    return render_template('carrinho.html', id_cliente=id_cliente)


@app.route('/editar/<id_cliente>', methods=['GET', 'POST'])
def editar(id_cliente):
    # coletando o nome da antiga imagem no bd.
    if request.method == 'POST':
        arquivo = db.session.execute(db.select(ImagemPerfil)).all()
        nome_da_imagem_antiga = arquivo[0][0].nome_imagem

        # recebendo post do arquivo para upload
        imagem = request.files.get('upload')



        if imagem:

            # adquirindo nome do arquivo do upload
            nome_imagem = imagem.filename

            # removendo a imagem antiga do diretório.
            path = "./static/imagem"
            dir = os.listdir(path)
            for i in dir:
                if nome_da_imagem_antiga == i:
                    os.remove('{}/{}'.format(path, nome_da_imagem_antiga))

            # salvando arquivo/imagem nova na pasta static.
            diretorio = './static/imagem'
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
            email = i[0].email
            nome = i[0].apelido
            cliente.append(i)

    """ Dados dos produtos """
    produto = []
    for i in carrinho:
        if id_cliente == i[0].id_cliente:
            produto.append(int(i[0].id_produto))

    # recebendo a data atual
    data_pedido = date.today().strftime('%d/%m/%Y')

    """ Somando o numero do pedido, para não sair um pedido com o mesmo numero que outro."""
    if pedidos:
        for i in pedidos:
            numero_pedido = i[0].numero_pedido + 1
    else:
        numero_pedido = 1

    status = 'Preparando'

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


        enviar_email_confirmaPedido(nome=nome, email_destinatario=email, dados_do_pedido=dados_do_pedido, todos_os_produtos=todos_os_produtos)

        return render_template('confirmacao.html', id_cliente=id_cliente, dados_do_pedido=dados_do_pedido,
                               produtos=produtos, cliente=cliente)

    return render_template('pedido.html', id_cliente=id_cliente)


@app.route('/controle_pedidos/<id_cliente>', methods=['GET', 'POST'])
def controle_pedidos(id_cliente):
    pedidos = db.session.execute(db.select(Pedido)).all()
    produtos = db.session.execute(db.select(Produto)).all()
    clientes = db.session.execute(db.select(Cliente)).all()
    endereco = db.session.execute(db.select(Endereco)).all()

    lista_pedidos = []
    verificar = ''
    for pedido in pedidos:
        for cliente in clientes:
            if pedido[0].id_cliente == cliente[0].apelido:
                if verificar != pedido[0].numero_pedido:
                    dados_pedido = {"numero_pedido": pedido[0].numero_pedido, "valor": pedido[0].valor,
                                    "id_cliente": pedido[0].id_cliente,
                                    "cep": cliente[0].cep_cliente, "status": pedido[0].status,
                                    "id_pedido": pedido[0].id_pedido, "data_pedido": pedido[0].data_pedido}
                    lista_pedidos.insert(0, dados_pedido)
                    verificar = pedido[0].numero_pedido

    return render_template('controle_pedidos.html', lista_pedidos=lista_pedidos, id_cliente=id_cliente, pedidos=pedidos,
                           produtos=produtos, clientes=clientes, endereco=endereco)


@app.route('/atualizar_status/<id_cliente>/<numero_pedido>/<id_pedido>', methods=['GET', 'POST'])
def atualizar_status(id_cliente, numero_pedido, id_pedido):
    pedidos = db.session.execute(db.select(Pedido)).all()
    clientes = db.session.execute(db.select(Cliente)).all()

    if request.method == 'POST':
        resposta_atualizacao = request.form.get('radio1')

        """ Atualiza o status do pedido de acordo com a opção do usuário """
        if resposta_atualizacao == 'option1':

            """ verifica se o numero do id_pedido enviado por parâmetro, é o mesmo que o id_pedido do banco de 
            dados Pedido."""
            for pedido in pedidos:
                id_pedido = int(id_pedido)
                if pedido[0].id_pedido == id_pedido:

                    """ agora verifica se o apelido enviado é o mesmo, que o apelido no banco de dados Cliente. """
                    for cliente in clientes:
                        if cliente[0].apelido == pedido[0].id_cliente:

                            """ busca todos os pedidos comm o numero de pedido enviado por parâmetro"""
                            todos_os_produtos_do_pedido = Pedido.query.filter_by(numero_pedido=numero_pedido).all()

                            """ atualiza o status de todos os pedidos encontrados. """
                            for produto in todos_os_produtos_do_pedido:
                                Pedido.query.filter_by(id_pedido=produto.id_pedido).update(
                                    {'id_cliente': f"{cliente[0].apelido}", 'id_produto': f"{produto.id_produto}",
                                     'data_pedido': f"{produto.data_pedido}", "valor": f"{produto.valor}",
                                     "status": "Preparando"})
                                db.session.commit()
                                numero_pedido = produto.numero_pedido
                            enviar_email_status(status='Preparando', pedido=numero_pedido,
                                                    nome=cliente[0].apelido,
                                                    email_destinatario=cliente[0].email)
                            return redirect(url_for('controle_pedidos', id_cliente=id_cliente))

        elif resposta_atualizacao == 'option2':
            """verifica se o numero do id_pedido enviado por parâmetro, é o mesmo que o id_pedido do banco de dados 
            Pedido. """
            for pedido in pedidos:
                id_pedido = int(id_pedido)
                if pedido[0].id_pedido == id_pedido:
                    """ agora verifica se o apelido enviado é o mesmo, que o apelido no banco de dados Cliente. """
                    for cliente in clientes:
                        if cliente[0].apelido == pedido[0].id_cliente:
                            """ busca todos os pedidos comm o numero de pedido enviado por parâmetro"""
                            todos_os_produtos_do_pedido = Pedido.query.filter_by(numero_pedido=numero_pedido).all()
                            """ atualiza o status de todos os pedidos encontrados. """
                            for produto in todos_os_produtos_do_pedido:
                                Pedido.query.filter_by(id_pedido=produto.id_pedido).update(
                                    {'id_cliente': f"{cliente[0].apelido}", 'id_produto': f"{produto.id_produto}",
                                     'data_pedido': f"{produto.data_pedido}", "valor": f"{produto.valor}",
                                     "status": "Saiu p/ Entrega"})
                                db.session.commit()
                                numero_pedido = produto.numero_pedido
                            enviar_email_status(status='Saiu p/ Entrega', pedido=numero_pedido, nome=cliente[0].apelido,
                                                    email_destinatario=cliente[0].email)
                            return redirect(url_for('controle_pedidos', id_cliente=id_cliente))

        elif resposta_atualizacao == 'option3':
            """ verifica se o numero do id_pedido enviado por parâmetro, é o mesmo que o id_pedido do banco de dados
             Pedido."""
            for pedido in pedidos:
                id_pedido = int(id_pedido)
                if pedido[0].id_pedido == id_pedido:
                    """ agora verifica se o apelido enviado é o mesmo, que o apelido no banco de dados Cliente. """
                    for cliente in clientes:
                        if cliente[0].apelido == pedido[0].id_cliente:
                            """ busca todos os pedidos comm o numero de pedido enviado por parâmetro"""
                            todos_os_produtos_do_pedido = Pedido.query.filter_by(numero_pedido=numero_pedido).all()
                            """ atualiza o status de todos os pedidos encontrados. """
                            for produto in todos_os_produtos_do_pedido:
                                Pedido.query.filter_by(id_pedido=produto.id_pedido).update(
                                    {'id_cliente': f"{cliente[0].apelido}", 'id_produto': f"{produto.id_produto}",
                                     'data_pedido': f"{produto.data_pedido}", "valor": f"{produto.valor}",
                                     "status": "Finalizado"})
                                db.session.commit()
                                numero_pedido = produto.numero_pedido
                            enviar_email_status(status='Finalizado', pedido=numero_pedido, nome=cliente[0].apelido,
                                                    email_destinatario=cliente[0].email)

                            return redirect(url_for('controle_pedidos', id_cliente=id_cliente))

        if resposta_atualizacao == 'option4':
            """ verifica se o numero do id_pedido enviado por parâmetro, é o mesmo que o id_pedido do banco de dados
             Pedido."""
            for pedido in pedidos:
                id_pedido = int(id_pedido)
                if pedido[0].id_pedido == id_pedido:
                    """ agora verifica se o apelido enviado é o mesmo, que o apelido no banco de dados Cliente. """
                    for cliente in clientes:
                        if cliente[0].apelido == pedido[0].id_cliente:
                            """ busca todos os pedidos comm o numero de pedido enviado por parâmetro"""
                            todos_os_produtos_do_pedido = Pedido.query.filter_by(numero_pedido=numero_pedido).all()
                            """ atualiza o status de todos os pedidos encontrados. """
                            for produto in todos_os_produtos_do_pedido:
                                Pedido.query.filter_by(id_pedido=produto.id_pedido).update(
                                    {'id_cliente': f"{cliente[0].apelido}", 'id_produto': f"{produto.id_produto}",
                                     'data_pedido': f"{produto.data_pedido}", "valor": f"{produto.valor}",
                                     "status": "Cancelado"})
                                db.session.commit()
                                numero_pedido = produto.numero_pedido
                            enviar_email_status(status='Cancelado',pedido=numero_pedido, nome=cliente[0].apelido, email_destinatario=cliente[0].email)
                            return redirect(url_for('controle_pedidos', id_cliente=id_cliente))

    return redirect(url_for('controle_pedidos', id_cliente=id_cliente))


@app.route('/perfil/<id_cliente>', methods=['GET', 'POST'])
def perfil(id_cliente):

    if request.method == 'POST':
        email = request.form.get('email')
        apelido = request.form.get('apelido')
        cep_cliente = request.form.get('cep_cliente')
        estado = request.form.get('estado')
        cidade = request.form.get('cidade')
        bairro = request.form.get('bairro')
        logradouro = request.form.get('logradouro')
        complemento = request.form.get('complemento')

        Cliente.query.filter_by(id_cliente=apelido).update(
            {'email': f"{email}", 'apelido': f"{apelido}",
             'cep_cliente': f"{cep_cliente}"})
        db.session.commit()

        Endereco.query.filter_by(id_cliente=apelido).update(
            {'cep_cliente': f"{cep_cliente}", 'estado': f"{estado}",
             'cidade': f"{cidade}", 'bairro': f"{bairro}", 'logradouro': f"{logradouro}",
             'complemento': f"{complemento}"})
        db.session.commit()

        mensagem = f'{id_cliente}, Seus Dados Foram Editados com Sucesso.'
        flash(mensagem)
        return redirect(url_for('perfil', id_cliente=id_cliente))


    clientes = db.session.execute(db.select(Cliente)).all()
    endereco = db.session.execute(db.select(Endereco)).all()


    return render_template('perfil.html', id_cliente=id_cliente, clientes=clientes, endereco=endereco)


@app.route('/editar_perfil/<id_cliente>', methods=['GEt', 'POST'])
def editar_perfil(id_cliente):

    clientes = db.session.execute(db.select(Cliente)).all()
    endereco = db.session.execute(db.select(Endereco)).all()

    return render_template('editar_perfil.html', id_cliente=id_cliente, clientes=clientes, endereco=endereco)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
    with app.app_context():
        db.create_all()
