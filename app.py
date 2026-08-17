import os
from functools import wraps
from flask import Flask, redirect, url_for, flash
from flask_login import LoginManager, current_user
from config import Config
from models import db, User
from storage import get_storage


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Faça login para continuar.'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # Storage de arquivos disponível em qualquer rota via current_app.extensions['storage']
    with app.app_context():
        app.extensions['storage'] = get_storage(app)

    # --- Blueprints (cada arquivo de rotas cuida de uma parte do site) ---
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.stores import stores_bp
    from routes.service_orders import service_orders_bp
    from routes.costs import costs_bp
    from routes.documents import documents_bp
    from routes.users import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(stores_bp)
    app.register_blueprint(service_orders_bp)
    app.register_blueprint(costs_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(users_bp)

    with app.app_context():
        db.create_all()
        _seed_first_admin()

    return app


def _seed_first_admin():
    """Se não existir NENHUM usuário ainda, cria um admin padrão
    pra você conseguir entrar pela primeira vez.
    Login: admin@ginseng.com | Senha: admin123
    TROQUE A SENHA assim que entrar pela primeira vez!"""
    if User.query.count() == 0:
        admin = User(name='Administrador', email='admin@ginseng.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('>>> Usuário admin criado: admin@ginseng.com / admin123 (troque a senha!)')


def admin_required(f):
    """Decorator: usa em cima de rotas que só admin pode acessar
    (criar, editar, excluir)."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('Você não tem permissão para fazer isso. Fale com um administrador.', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return wrapper


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
