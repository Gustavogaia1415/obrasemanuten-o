"""
Camada de armazenamento de arquivos.

A ideia aqui é isolar "onde os arquivos ficam guardados" numa única peça do
código. Assim, quando você quiser trocar de 'local' pra 'supabase', não
precisa mexer em nenhuma rota — só troca STORAGE_BACKEND no .env e configura
as credenciais do Supabase.
"""
import os
import uuid
from werkzeug.utils import secure_filename


class LocalStorage:
    """Guarda os arquivos numa pasta dentro do próprio servidor.
    Bom pra testar no seu PC. NÃO use em produção com Render free tier -
    os arquivos podem sumir quando o serviço reinicia/atualiza."""

    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)

    def save(self, file_storage):
        original_name = secure_filename(file_storage.filename)
        unique_name = f"{uuid.uuid4().hex}_{original_name}"
        path = os.path.join(self.upload_folder, unique_name)
        file_storage.save(path)
        # URL relativa servida pelo Flask via /static/uploads/<nome>
        url = f"/static/uploads/{unique_name}"
        return {
            'filename': original_name,
            'storage_path': unique_name,
            'url': url,
        }

    def delete(self, storage_path):
        path = os.path.join(self.upload_folder, storage_path)
        if os.path.exists(path):
            os.remove(path)


class SupabaseStorage:
    """Guarda os arquivos no Supabase Storage (recomendado pra produção).
    Requer: pip install supabase
    Configure SUPABASE_URL, SUPABASE_KEY e SUPABASE_BUCKET no .env.
    """

    def __init__(self, url, key, bucket):
        from supabase import create_client
        self.client = create_client(url, key)
        self.bucket = bucket

    def save(self, file_storage):
        original_name = secure_filename(file_storage.filename)
        unique_name = f"{uuid.uuid4().hex}_{original_name}"
        file_bytes = file_storage.read()
        self.client.storage.from_(self.bucket).upload(unique_name, file_bytes)
        url = self.client.storage.from_(self.bucket).get_public_url(unique_name)
        return {
            'filename': original_name,
            'storage_path': unique_name,
            'url': url,
        }

    def delete(self, storage_path):
        self.client.storage.from_(self.bucket).remove([storage_path])


def get_storage(app):
    """Retorna o backend de storage certo, de acordo com a config do app."""
    if app.config['STORAGE_BACKEND'] == 'supabase':
        return SupabaseStorage(
            app.config['SUPABASE_URL'],
            app.config['SUPABASE_KEY'],
            app.config['SUPABASE_BUCKET'],
        )
    return LocalStorage(app.config['UPLOAD_FOLDER'])
