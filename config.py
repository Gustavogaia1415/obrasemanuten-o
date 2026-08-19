import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()  # lê o arquivo .env, se existir, e carrega as variáveis dele

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Chave secreta usada pelo Flask pra proteger sessões/cookies.
    # Em produção, defina isso como variável de ambiente (nunca deixe fixo no código).
    SECRET_KEY = os.environ.get('SECRET_KEY', 'troque-essa-chave-antes-de-colocar-no-ar')

    # Banco de dados. Por padrão usa um arquivo SQLite local (bom pra testar no seu PC).
    # Quando for pra produção, defina DATABASE_URL (ex: Postgres do Neon/Supabase/Render).
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f"sqlite:///{os.path.join(basedir, 'app.db')}"
    )
    # Corrige um detalhe: alguns provedores dão a URL como "postgres://",
    # mas o SQLAlchemy moderno exige "postgresql://". Isso ajusta automaticamente.
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            'postgres://', 'postgresql://', 1
        )
    # Usa o driver psycopg (versão 3), que já está no requirements.txt.
    if SQLALCHEMY_DATABASE_URI.startswith('postgresql://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            'postgresql://', 'postgresql+psycopg://', 1
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Upload de arquivos ---
    # 'local'  -> guarda os arquivos numa pasta do próprio servidor (só pra teste/dev).
    # 'supabase' -> guarda no Supabase Storage (recomendado pra produção, veja README).
    STORAGE_BACKEND = os.environ.get('STORAGE_BACKEND', 'local')

    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB por arquivo

    # Credenciais do Supabase Storage (só usadas se STORAGE_BACKEND == 'supabase')
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
    SUPABASE_BUCKET = os.environ.get('SUPABASE_BUCKET', 'documentos')

    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)