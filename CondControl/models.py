from datetime import datetime
from sqlalchemy.orm import joinedload
from database import db  # Importando o db do novo arquivo
from flask import Flask, jsonify, request
from flask_login import UserMixin, current_user, login_required, login_user, logout_user
from sqlalchemy import (
    DECIMAL,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)


class Morador(UserMixin, db.Model):  # Herda de UserMixin
    __tablename__ = 'moradores'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    moradia = db.Column(db.String(100), nullable=False)
    apartamento = db.Column(db.String(50), nullable=False)
    senha = db.Column(db.String(128), nullable=False)

    def get_id(self):
        return str(self.id)

def get_user_by_username(username):
    # Aqui, você busca o morador pelo email, que é o usuário
    return Morador.query.filter_by(email=username).first()

class Financa(db.Model):
    __tablename__ = 'financas'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.Enum('Receita', 'Despesa'), nullable=False)
    descricao = db.Column(db.String(255))
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data = db.Column(db.Date, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    morador_id = db.Column(db.Integer, db.ForeignKey('moradores.id'))

class AreaComum(db.Model):
    __tablename__ = 'areas_comuns'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    capacidade = db.Column(db.Integer, nullable=True)
    disponivel = db.Column(db.Boolean, default=True)
    quantidade = db.Column(db.Integer, nullable=False)
    imagem = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<AreaComum {self.nome}>'

class Reserva(db.Model):
    __tablename__ = 'reservas'
    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey('areas_comuns.id'), nullable=False)
    morador_id = db.Column(db.Integer, db.ForeignKey('moradores.id'), nullable=False)
    data_reserva = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum('Pendente', 'Confirmada', 'Cancelada'), default='Pendente')

class Comunicado(db.Model):
    __tablename__ = 'comunicados'  # Nome da tabela no banco de dados
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(100), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=True)
    morador_id = db.Column(db.Integer, db.ForeignKey('moradores.id'), nullable=True)
    status = db.Column(db.String(50), default='Ativo', nullable=True)

    def serialize(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'mensagem': self.mensagem,
            'data_publicacao': self.data_envio.strftime("%Y-%m-%d %H:%M:%S"),  # Formata a data
            'status': self.status
        }

class Ocorrencia(db.Model):
    __tablename__ = 'ocorrencias'

    id = db.Column(db.Integer, primary_key=True)
    morador_id = db.Column(db.Integer, db.ForeignKey('moradores.id'), nullable=False)
    tipo = db.Column(db.Enum('Reclamação', 'Incidente', 'Sugestão', name='tipo_ocorrencia_enum'), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('Aberta', 'Em andamento', 'Resolvida', name='status_ocorrencia_enum'), default='Aberta')
    titulo_ocorrencia = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Ocorrencia {self.titulo_ocorrencia} - Status: {self.status} - Data: {self.data} - Morador ID: {self.morador_id}>"


class Visitante(db.Model):
    __tablename__ = 'visitantes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(50))
    morador_id = db.Column(db.Integer, db.ForeignKey('moradores.id'), nullable=False)
    data_entrada = db.Column(db.DateTime, default=db.func.current_timestamp())
    data_saida = db.Column(db.DateTime)

    morador = db.relationship('Morador', backref='visitantes')  # Adicionando o relacionamento aqui
    
class TaxaCondominio(db.Model):
    __tablename__ = 'taxas_condominio'
    
    id = db.Column(db.Integer, primary_key=True)
    condominio_id = db.Column(db.Integer, nullable=False)  # Referência ao ID do condomínio
    valor = db.Column(db.Float, nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pendente')  # Status da taxa (pendente, paga, etc.)

    def __repr__(self):
        return f'<Taxa {self.condominio_id} - R$ {self.valor} - Vencimento: {self.data_vencimento}>'


class Manutencao(db.Model):
    __tablename__ = 'manutencao'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    data_programada = db.Column(db.Date, nullable=False)  # Alterado para data_programada
    custo_estimado = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=True, default='programada')

    def __repr__(self):
        return f'<Manutencao {self.id} - {self.descricao}>'


    
class Despesa(db.Model):
    __tablename__ = 'despesas'  # Certifique-se de que o nome está correto
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data = db.Column(db.Date, nullable=False)
    categoria = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Despesa {self.descricao}, Valor: {self.valor}>"



class Receita(db.Model):
    __tablename__ = 'receitas'

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data = db.Column(db.Date, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)  # Alterado aqui

    def __repr__(self):
        return f'<Receita {self.descricao}>'




class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    receitas = db.relationship('Receita', backref='categoria', lazy=True)