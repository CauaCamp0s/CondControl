import secrets  # Para gerar tokens
from functools import wraps
from sqlalchemy.orm import joinedload
from database import db
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from models import *  # Importa os modelos do banco de dados (assumindo que estão definidos no models.py)
from werkzeug.security import check_password_hash, generate_password_hash

# Inicializa o aplicativo Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:140610@localhost/condominio_db'
app.config['SECRET_KEY'] = 'sua_chave_secreta'
db.init_app(app)

# Inicializa o gerenciador de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Dicionários para gerenciamento de usuários e tokens de redefinição de senha
users = {}
password_reset_tokens = {}

# Classe para o modelo de usuário
class User(UserMixin):
    # Adicione suas colunas aqui
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return Morador.query.get(int(user_id))

# Função para buscar um comunicado por ID
def get_comunicado_by_id(comunicado_id):
    return Comunicado.query.get(comunicado_id)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # Verifica se o ID do usuário está na sessão
            flash('Você precisa estar logado para acessar essa página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Função para atualizar um comunicado
def update_comunicado(comunicado_id, titulo, descricao, status):
    comunicado = get_comunicado_by_id(comunicado_id)
    if comunicado:
        comunicado.titulo = titulo
        comunicado.descricao = descricao
        comunicado.status = status
        db.session.commit()  # Não se esqueça de commitar as alterações no banco de dados

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        telefone = request.form.get('telefone')
        moradia = request.form.get('moradia')
        apartamento = request.form.get('apartamento')

        # Gera o hash da senha
        hashed_senha = generate_password_hash(senha, method='pbkdf2:sha256')

        # Lógica para inserir no banco de dados
        try:
            novo_morador = Morador(
                nome=nome,
                email=email,
                telefone=telefone,
                moradia=moradia,
                apartamento=apartamento,
                senha=hashed_senha  # Use a senha hasheada aqui
            )
            db.session.add(novo_morador)
            db.session.commit()
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('index'))  # Redireciona para a página inicial
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar o morador. Detalhes: {str(e)}', 'danger')
    
    return render_template('register.html')  # Retorna o template do registro


# Roteamento e Lógica de Autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = get_user_by_username(username)

        if user and check_password_hash(user.senha, password):
            login_user(user)  # Use login_user para autenticar o usuário
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'warning')

    return render_template('login.html')

@app.route('/ocorrencias', methods=['GET', 'POST'])
@login_required
def cadastrar_ocorrencia():
    if current_user.is_authenticated:
        morador_id = current_user.id  # Só tenta acessar o id se o usuário estiver autenticado
    else:
        flash('Você precisa estar logado para registrar uma ocorrência.', 'danger')
        return redirect(url_for('login'))  # Redireciona para a página de login se não estiver autenticado

    if request.method == 'POST':
        # Processar o formulário
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        tipo_ocorrencia = request.form['tipo_ocorrencia']
        data_hora = request.form['data_hora']
        anexo = request.files.get('anexo')

        nova_ocorrencia = Ocorrencia(
            titulo=titulo,
            descricao=descricao,
            tipo_ocorrencia=tipo_ocorrencia,
            data_hora=datetime.strptime(data_hora, '%Y-%m-%d %H:%M'),  # Certifique-se que o formato da data seja compatível
            morador_id=morador_id  # Use morador_id aqui
        )

        db.session.add(nova_ocorrencia)
        db.session.commit()
        flash("Ocorrência registrada com sucesso!", "success")
        return redirect(url_for('cadastrar_ocorrencia'))

    # Para o método GET
    ocorrencias = Ocorrencia.query.all()
    return render_template('ocorrencias.html', ocorrencias=ocorrencias)



@app.route('/index')
@login_required
def index():
    return render_template('index.html')  # Sua página inicial após login

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Roteamento para Redefinição de Senha
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        if email in users:
            token = secrets.token_urlsafe(16)
            password_reset_tokens[token] = email
            flash('Um email foi enviado com instruções para redefinir sua senha.')  # Simular envio de email
            print(f"Token gerado (simulação de email): {token}")
        else:
            flash('Email não encontrado.')
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = password_reset_tokens.get(token)
    if not email:
        flash('Token inválido ou expirado.')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash('As senhas não coincidem.')
            return render_template('reset_password.html', token=token)
        
        users[email]['password'] = generate_password_hash(new_password)
        del password_reset_tokens[token]  # Remove o token após o uso
        flash('Senha redefinida com sucesso. Você pode fazer login agora.')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

# Roteamento para Áreas Comuns
@app.route('/areas', methods=['GET'])
def get_areas():
    areas = AreaComum.query.all()
    areas_list = [
        {
            'id': area.id,
            'nome': area.nome,
            'descricao': area.descricao,
            'capacidade': area.capacidade,
            'disponivel': area.disponivel,
            'quantidade': area.quantidade,
            'imagem': area.imagem
        }
        for area in areas
    ]
    return jsonify(areas_list)

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/reservas', methods=['GET', 'POST'])
@login_required
def gerenciar_reservas():
    if request.method == 'POST':
        area_id = request.form['area_id']
        morador_id = request.form['morador_id']
        data_reserva = request.form['data_reserva']
        hora_inicio = request.form['hora_inicio']
        hora_fim = request.form['hora_fim']

        # Validação de dados
        if not all([area_id, morador_id, data_reserva, hora_inicio, hora_fim]):
            flash('Por favor, preencha todos os campos.')
            return redirect(url_for('gerenciar_reservas'))

        # Cria uma nova reserva
        nova_reserva = Reserva(
            area_id=area_id,
            morador_id=morador_id,
            data_reserva=data_reserva,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim
        )
        db.session.add(nova_reserva)
        try:
            db.session.commit()
            flash('Reserva criada com sucesso!')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar reserva: ' + str(e))
        return redirect(url_for('gerenciar_reservas'))
    
    reservas = Reserva.query.join(AreaComum).join(Morador).add_columns(
        Reserva.data_reserva, 
        Reserva.hora_inicio, 
        Reserva.hora_fim,
        AreaComum.nome.label('area_nome'),
        Morador.nome.label('morador_nome'),
        Morador.moradia.label('morador_moradia')
    ).all()

    return render_template('reservas.html', reservas=reservas)

@app.route('/manutencao')
@login_required
def listar_manutencoes():
    manutencoes = Manutencao.query.all()
    return render_template('manutencao.html', manutencoes=manutencoes)

@app.route('/manutencao/adicionar', methods=['POST'])
@login_required
def adicionar_manutencao():
    descricao = request.form.get('descricao-manutencao')
    data = request.form.get('data-manutencao')
    custo = request.form.get('custo-manutencao')

    # Validação de dados
    if not all([descricao, data, custo]):
        flash('Por favor, preencha todos os campos.')
        return redirect(url_for('listar_manutencoes'))

    nova_manutencao = Manutencao(
        descricao=descricao,
        data=datetime.strptime(data, '%Y-%m-%d'),
        custo=float(custo)
    )
    
    db.session.add(nova_manutencao)
    try:
        db.session.commit()
        flash('Manutenção adicionada com sucesso!')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao adicionar manutenção: ' + str(e))
    return redirect(url_for('listar_manutencoes'))

@app.route('/manutencao/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_manutencao(id):
    manutencao = Manutencao.query.get_or_404(id)
    if request.method == 'POST':
        manutencao.descricao = request.form['descricao']
        manutencao.data = datetime.strptime(request.form['data'], '%Y-%m-%d')
        manutencao.custo = float(request.form['custo'])
        try:
            db.session.commit()
            flash('Manutenção atualizada com sucesso!')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar manutenção: ' + str(e))
        return redirect(url_for('listar_manutencoes'))
    
    return render_template('edit_manutencao.html', manutencao=manutencao)

@app.route('/manutencao/delete/<int:id>', methods=['POST'])
@login_required
def excluir_manutencao(id):
    manutencao = Manutencao.query.get_or_404(id)
    db.session.delete(manutencao)
    try:
        db.session.commit()
        flash('Manutenção excluída com sucesso!')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir manutenção: ' + str(e))
    return redirect(url_for('listar_manutencoes'))

@app.route('/api/dados-financeiros', methods=['GET'])
def dados_financeiros():
    """Retorna os dados financeiros em formato JSON."""
    receitas = Receita.query.all()
    despesas = Despesa.query.all()

    dados = {
        'receitas': [{'descricao': r.descricao, 'valor': r.valor, 'data': r.data.strftime('%Y-%m-%d')} for r in receitas],
        'despesas': [{'descricao': d.descricao, 'valor': d.valor, 'data': d.data.strftime('%Y-%m-%d')} for d in despesas],
    }
    return jsonify(dados)


@app.route('/api/receitas', methods=['POST'])
def adicionar_receita():
    """Adiciona uma nova receita."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400

    try:
        descricao = data['descricao']
        valor = float(data['valor'])
        data_receita = data['data']
        categoria = data['categoria']
        
        # Mapeamento para categoria_id
        categoria_id_map = {
            'taxa': 1,
            'aluguel': 2,
            'outra': 3
        }

        if categoria not in categoria_id_map:
            return jsonify({'error': 'Categoria inválida'}), 400
        
        categoria_id = categoria_id_map[categoria]

        # Verifica se a receita já existe
        receita_existente = Receita.query.filter_by(
            descricao=descricao,
            valor=valor,
            data=data_receita,
            categoria_id=categoria_id
        ).first()

        if receita_existente:
            return jsonify({'error': 'Receita já existe.'}), 409

        nova_receita = Receita(
            descricao=descricao,
            valor=valor,
            data=data_receita,
            categoria_id=categoria_id
        )
        db.session.add(nova_receita)
        db.session.commit()

        return jsonify({'message': 'Receita adicionada com sucesso!'}), 201
    
    except KeyError as e:
        return jsonify({'error': f'Campo ausente: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': f'Erro de conversão: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/despesas', methods=['POST'])
def adicionar_despesa():
    """Adiciona uma nova despesa."""
    data = request.get_json()
    nova_despesa = Despesa(
        descricao=data['descricao'],
        valor=data['valor'],
        data=data['data'],
        categoria=data['categoria']
    )
    db.session.add(nova_despesa)
    db.session.commit()
    return jsonify({'message': 'Despesa adicionada com sucesso!'}), 201


@app.route('/ver-receitas')
def ver_receitas():
    """Exibe todas as receitas cadastradas."""
    receitas = Receita.query.all()
    categorias = Categoria.query.all()
    return render_template('ver_receitas.html', receitas=receitas, categorias=categorias)


@app.route('/ver-registros')
def ver_registros():
    """Exibe todos os registros de manutenção."""
    manutencoes = Manutencao.query.all()
    return render_template('ver_registros.html', manutencoes=manutencoes)

@app.route('/editar_receita/<int:id>', methods=['GET', 'POST'])
def editar_receita(id):
    receita = Receita.query.get_or_404(id)
    categorias = Categoria.query.all()  # Buscando todas as categorias

    if request.method == 'POST':
        receita.descricao = request.form['descricao']
        receita.valor = request.form['valor']
        receita.data = request.form['data']
        receita.categoria_id = request.form['categoria']  # Atualizando a categoria

        db.session.commit()
        return redirect(url_for('ver_receitas'))

    return render_template('editar_receita.html', receita=receita, categorias=categorias)


@app.route('/excluir-receita/<int:id>', methods=['POST'])
def excluir_receita(id):
    receita = Receita.query.get_or_404(id)
    db.session.delete(receita)
    db.session.commit()
    flash('Receita excluída com sucesso!', 'success')  # Adicionando feedback ao usuário
    return redirect(url_for('ver_receitas'))


@app.route('/confirmar-exclusao-receita/<int:id>', methods=['GET'])
def confirmar_exclusao_receita(id):
    receita = Receita.query.get_or_404(id)
    return render_template('confirmar_exclusao.html', receita=receita)


@app.route('/ver-despesas', methods=['GET'])
def ver_despesas():
    despesas = Despesa.query.all()
    return render_template('ver_despesas.html', despesas=despesas)


@app.route('/editar-despesa/<int:id>', methods=['GET', 'POST'])
def editar_despesa(id):
    despesa = Despesa.query.get_or_404(id)

    if request.method == 'POST':
        despesa.descricao = request.form['descricao']
        despesa.valor = request.form['valor']
        despesa.data = request.form['data']
        despesa.categoria = request.form['categoria']
        
        db.session.commit()
        flash('Despesa atualizada com sucesso!', 'success')  # Feedback ao usuário
        return redirect(url_for('ver_despesas'))

    return render_template('editar_despesa.html', despesa=despesa)


@app.route('/excluir-despesa/<int:id>', methods=['POST'])
def excluir_despesa(id):
    despesa = Despesa.query.get_or_404(id)
    db.session.delete(despesa)
    db.session.commit()
    flash('Despesa excluída com sucesso!', 'success')  # Feedback ao usuário
    return redirect(url_for('ver_despesas'))


@app.route('/dashboard')
def dashboard():
    # Coleta dados de receitas, despesas e transações
    receitas_totais = Receita.query.with_entities(db.func.sum(Receita.valor)).scalar() or 0.0
    despesas_totais = Despesa.query.with_entities(db.func.sum(Despesa.valor)).scalar() or 0.0
    transacoes = []  # Aqui você pode coletar as últimas transações, se necessário
    manutencoes = Manutencao.query.all()  # Coletando todas as manutenções

    return render_template('dashboard.html', 
                           total_receitas=receitas_totais,
                           total_despesas=despesas_totais,
                           transacoes=transacoes,
                           manutencoes=manutencoes)


@app.route('/financeiro')
def financeiro():
    return render_template('financeiro.html')


@app.route('/comunicados')
def comunicados():
    comunicados = Comunicado.query.all()  # Obtém todos os comunicados do banco de dados
    return render_template('comunicados.html', comunicados=comunicados)


@app.route('/edit_comunicado/<int:comunicado_id>', methods=['GET'])
def edit_comunicado(comunicado_id):
    comunicado = Comunicado.query.get(comunicado_id)  # Obtém o comunicado pelo ID
    
    if comunicado:
        return render_template('edit_comunicado.html', comunicado=comunicado)
    
    flash('Comunicado não encontrado', 'error')
    return redirect(url_for('comunicados'))


@app.route('/salvar_comunicado/<int:comunicado_id>', methods=['POST'])
def salvar_comunicado(comunicado_id):
    titulo = request.form['titulo']
    descricao = request.form['descricao']
    status = request.form['status']

    comunicado = Comunicado.query.get(comunicado_id)
    if comunicado:
        comunicado.titulo = titulo
        comunicado.descricao = descricao
        comunicado.status = status
        db.session.commit()
        flash('Comunicado atualizado com sucesso!', 'success')
    else:
        flash('Comunicado não encontrado!', 'danger')

    return redirect(url_for('comunicados'))


@app.route('/excluir_comunicado/<int:comunicado_id>', methods=['POST'])
def excluir_comunicado(comunicado_id):
    comunicado = Comunicado.query.get(comunicado_id)
    if comunicado:
        db.session.delete(comunicado)
        db.session.commit()
        flash('Comunicado excluído com sucesso!', 'success')
    else:
        flash('Comunicado não encontrado!', 'danger')
    
    return redirect(url_for('comunicados'))


@app.route('/adicionar_comunicado', methods=['GET', 'POST'])
def adicionar_comunicado():
    if request.method == 'POST':
        titulo = request.form['titulo']
        mensagem = request.form['mensagem']
        status = request.form['status']

        novo_comunicado = Comunicado(titulo=titulo, descricao=mensagem, status=status)
        db.session.add(novo_comunicado)
        db.session.commit()
        flash('Comunicado adicionado com sucesso!', 'success')
        return redirect(url_for('comunicados'))
    
    return render_template('adicionar_comunicado.html')

@app.route('/editar_ocorrencia/<int:ocorrencia_id>', methods=['GET', 'POST'])
def editar_ocorrencia(ocorrencia_id):
    # Busca a ocorrência pelo ID fornecido
    ocorrencia = Ocorrencia.query.get_or_404(ocorrencia_id)

    if request.method == 'POST':
        # Atualiza os campos da ocorrência com os dados do formulário
        ocorrencia.titulo_ocorrencia = request.form['titulo']
        ocorrencia.descricao = request.form['descricao']
        ocorrencia.data = request.form['data']
        ocorrencia.tipo = request.form['tipo']  # Verifique se 'tipo' está no formulário
        ocorrencia.status = request.form['status']  # Verifique se 'status' está no formulário

        # Lógica para lidar com o anexo, se necessário
        if 'anexo' in request.files:
            anexo = request.files['anexo']
            if anexo.filename != '':
                # Salvar o anexo no servidor
                nome_anexo = f"{int(time.time())}_{anexo.filename}"  # Adiciona timestamp
                caminho_anexo = os.path.join('uploads', nome_anexo)
                anexo.save(caminho_anexo)
                ocorrencia.anexo = caminho_anexo  # Atualiza o caminho do anexo na ocorrência

        try:
            db.session.commit()  # Commit das alterações no banco de dados
            flash('Ocorrência atualizada com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()  # Rollback em caso de erro
            flash(f'Erro ao atualizar a ocorrência: {str(e)}', 'danger')

        return redirect(url_for('ocorrencias'))  # Redireciona para a lista de ocorrências

    # Renderiza o template com o formulário preenchido
    return render_template('editar_ocorrencia.html', ocorrencia=ocorrencia)


# Rota para excluir uma ocorrência
@app.route('/excluir_ocorrencia/<int:id>', methods=['POST'])
def excluir_ocorrencia(id):
    ocorrencia = Ocorrencia.query.get_or_404(id)
    db.session.delete(ocorrencia)
    db.session.commit()
    flash('Ocorrência excluída com sucesso!', 'success')
    return redirect(url_for('ocorrencias'))


@app.route('/visitantes', methods=['GET'])
def listar_visitantes():
    moradores = Morador.query.all()  # Busca todos os moradores
    visitantes = Visitante.query.options(joinedload(Visitante.morador)).all()  # Busca todos os visitantes

    print(moradores)  # Verifique os moradores
    print(visitantes)  # Verifique os visitantes

    # Renderiza a lista de moradores e visitantes no template
    return render_template('visitantes.html', moradores=moradores, visitantes=visitantes)


# Rota para registrar um novo visitante
@app.route('/registrar_visitante', methods=['POST'])
def registrar_visitante():
    nome = request.form['nome']
    documento = request.form['documento']
    data_entrada = request.form['data_entrada']
    morador_id = request.form['morador_id']

    # Cria um novo visitante e adiciona ao banco de dados
    novo_visitante = Visitante(nome=nome, documento=documento, data_entrada=data_entrada, morador_id=morador_id)
    db.session.add(novo_visitante)
    db.session.commit()

    flash('Visitante registrado com sucesso!', 'success')
    return redirect(url_for('listar_visitantes'))


# Rota para editar um visitante
@app.route('/visitantes/editar/<int:visitante_id>', methods=['GET', 'POST'])
def editar_visitante(visitante_id):
    visitante = Visitante.query.get_or_404(visitante_id)  # Obtém o visitante pelo ID

    if request.method == 'POST':
        # Atualiza os dados do visitante
        visitante.nome = request.form['nome']
        visitante.documento = request.form['documento']
        visitante.data_entrada = request.form['data_entrada']
        visitante.morador_id = request.form['morador_id']

        try:
            db.session.commit()  # Salva as alterações no banco de dados
            flash('Visitante atualizado com sucesso!', 'success')
            return redirect(url_for('listar_visitantes'))  # Redireciona para a lista de visitantes
        except Exception as e:
            db.session.rollback()  # Reverte se houver erro
            flash('Erro ao atualizar visitante. Tente novamente.', 'danger')

    moradores = Morador.query.all()  # Obtém todos os moradores
    return render_template('editar_visitante.html', visitante=visitante, moradores=moradores)


# Rota para excluir um visitante
@app.route('/excluir_visitante/<int:visitante_id>', methods=['POST'])
def excluir_visitante(visitante_id):
    visitante = Visitante.query.get_or_404(visitante_id)
    db.session.delete(visitante)
    db.session.commit()
    flash('Visitante excluído com sucesso!', 'success')
    return redirect(url_for('listar_visitantes'))

if __name__ == '__main__':
    # Adicione usuários de teste para simular o funcionamento
    users['testuser'] = {
        'password': generate_password_hash('testpassword')  # Hash da senha
    }
    users['admin'] = {
        'password': generate_password_hash('admin')  # Hash da senha admin
    }
    
    app.run(debug=True)