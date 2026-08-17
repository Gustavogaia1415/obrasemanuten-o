from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def gen_uuid():
    import uuid
    return str(uuid.uuid4())


class User(UserMixin, db.Model):
    """Usuário do sistema. is_admin = True -> pode criar/editar/excluir tudo.
    is_admin = False -> só pode visualizar."""
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_active(self):
        # Flask-Login usa isso pra saber se a conta pode logar.
        return self.active

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Store(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(10))
    phone = db.Column(db.String(30))
    manager = db.Column(db.String(120))
    status = db.Column(db.String(20), default='ativa')  # ativa | inativa | em_reforma
    monthly_budget = db.Column(db.Float, default=0)
    annual_budget = db.Column(db.Float, default=0)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    service_orders = db.relationship('ServiceOrder', backref='store', lazy=True)
    costs = db.relationship('MaintenanceCost', backref='store', lazy=True)
    documents = db.relationship('Document', backref='store', lazy=True)


class Supplier(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    name = db.Column(db.String(150), nullable=False)
    cnpj = db.Column(db.String(30))
    category = db.Column(db.String(30))
    contact_name = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    email = db.Column(db.String(120))
    address = db.Column(db.String(255))
    status = db.Column(db.String(20), default='ativo')  # ativo | inativo
    rating = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)


class ServiceOrder(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    code = db.Column(db.String(30), unique=True)
    request_code = db.Column(db.String(30))
    store_id = db.Column(db.String(36), db.ForeignKey('store.id'))
    supplier_id = db.Column(db.String(36), db.ForeignKey('supplier.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(30))
    custom_category = db.Column(db.String(100))
    selection_mode = db.Column(db.String(20), default='loja')
    status = db.Column(db.String(30), default='criada')
    priority = db.Column(db.String(20), default='media')
    estimated_cost = db.Column(db.Float, default=0)
    actual_cost = db.Column(db.Float, default=0)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    supplier = db.relationship('Supplier')


class MaintenanceCost(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    description = db.Column(db.String(255), nullable=False)
    store_id = db.Column(db.String(36), db.ForeignKey('store.id'), nullable=False)
    service_order_id = db.Column(db.String(36), db.ForeignKey('service_order.id'))
    service_order_code = db.Column(db.String(30))
    request_code = db.Column(db.String(30))
    supplier_id = db.Column(db.String(36), db.ForeignKey('supplier.id'))
    cost_type = db.Column(db.String(30))  # material | mao_de_obra | servico_terceirizado | emergencial | outros
    amount = db.Column(db.Float, nullable=False, default=0)
    date = db.Column(db.Date)
    invoice_number = db.Column(db.String(60))
    notes = db.Column(db.Text)
    category = db.Column(db.String(30))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    supplier = db.relationship('Supplier')
    service_order = db.relationship('ServiceOrder')


class CustomFolder(db.Model):
    """Pasta personalizada criada pelo usuário dentro de Documentos."""
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    name = db.Column(db.String(150), nullable=False)
    store_id = db.Column(db.String(36), db.ForeignKey('store.id'), nullable=False)
    parent_folder_id = db.Column(db.String(36), db.ForeignKey('custom_folder.id'), nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)


class Document(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    name = db.Column(db.String(200), nullable=False)
    store_id = db.Column(db.String(36), db.ForeignKey('store.id'), nullable=False)
    folder_type = db.Column(db.String(30))  # nota_fiscal | licenca | contrato | ... | personalizada
    custom_folder = db.Column(db.String(150))
    subfolder = db.Column(db.String(150))
    description = db.Column(db.Text)
    related_entity_type = db.Column(db.String(30))
    related_entity_id = db.Column(db.String(36))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    files = db.relationship('DocumentFile', backref='document', lazy=True, cascade='all, delete-orphan')


class DocumentFile(db.Model):
    """Cada arquivo físico anexado a um Document (um Document pode ter vários arquivos)."""
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    document_id = db.Column(db.String(36), db.ForeignKey('document.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)   # nome original do arquivo
    storage_path = db.Column(db.String(500), nullable=False)  # caminho/local ou chave no storage
    url = db.Column(db.String(500))  # URL pública, se houver (local ou Supabase)
    uploaded_date = db.Column(db.DateTime, default=datetime.utcnow)
