from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from models import db, Document, DocumentFile, Store, CustomFolder
from app import admin_required

documents_bp = Blueprint('documents', __name__, url_prefix='/documentos')

FOLDER_TYPE_LABELS = {
    'nota_fiscal': 'Nota Fiscal', 'licenca': 'Licença', 'contrato': 'Contrato',
    'manual': 'Manual', 'garantia': 'Garantia', 'laudo': 'Laudo',
    'alvara': 'Alvará', 'personalizada': 'Personalizada',
}


@documents_bp.route('/')
@login_required
def stores_grid():
    stores = Store.query.order_by(Store.name).all()
    counts = {s.id: Document.query.filter_by(store_id=s.id).count() for s in stores}
    return render_template('documents_stores.html', stores=stores, counts=counts)


@documents_bp.route('/loja/<store_id>')
@login_required
def folders_grid(store_id):
    store = Store.query.get_or_404(store_id)
    docs = Document.query.filter_by(store_id=store_id).all()
    custom_folders = CustomFolder.query.filter_by(store_id=store_id, parent_folder_id=None).all()

    folder_counts = {}
    for key in FOLDER_TYPE_LABELS:
        if key != 'personalizada':
            folder_counts[key] = len([d for d in docs if d.folder_type == key])

    custom_counts = {f.id: len([d for d in docs if d.custom_folder == f.name]) for f in custom_folders}

    return render_template('documents_folders.html', store=store, folder_labels=FOLDER_TYPE_LABELS,
                            folder_counts=folder_counts, custom_folders=custom_folders,
                            custom_counts=custom_counts)


@documents_bp.route('/loja/<store_id>/pasta/<folder_key>')
@login_required
def folder_docs(store_id, folder_key):
    store = Store.query.get_or_404(store_id)
    if folder_key.startswith('custom_'):
        folder_id = folder_key.replace('custom_', '')
        folder = CustomFolder.query.get_or_404(folder_id)
        docs = Document.query.filter_by(store_id=store_id, custom_folder=folder.name).all()
        folder_name = folder.name
    else:
        docs = Document.query.filter_by(store_id=store_id, folder_type=folder_key).all()
        folder_name = FOLDER_TYPE_LABELS.get(folder_key, folder_key)
    return render_template('documents_list.html', store=store, docs=docs,
                            folder_name=folder_name, folder_key=folder_key)


@documents_bp.route('/loja/<store_id>/pasta/<folder_key>/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def create(store_id, folder_key):
    store = Store.query.get_or_404(store_id)
    if request.method == 'POST':
        folder_type = folder_key if not folder_key.startswith('custom_') else 'personalizada'
        custom_folder_name = None
        if folder_key.startswith('custom_'):
            cf = CustomFolder.query.get(folder_key.replace('custom_', ''))
            custom_folder_name = cf.name if cf else None

        doc = Document(
            name=request.form['name'],
            store_id=store_id,
            folder_type=folder_type,
            custom_folder=custom_folder_name,
            subfolder=request.form.get('subfolder'),
            description=request.form.get('description'),
        )
        db.session.add(doc)
        db.session.flush()  # já gera doc.id sem precisar commitar ainda

        storage = current_app.extensions['storage']
        files = request.files.getlist('files')
        for f in files:
            if f and f.filename:
                result = storage.save(f)
                db.session.add(DocumentFile(
                    document_id=doc.id,
                    filename=result['filename'],
                    storage_path=result['storage_path'],
                    url=result['url'],
                ))
        db.session.commit()
        flash('Documento cadastrado!', 'success')
        return redirect(url_for('documents.folder_docs', store_id=store_id, folder_key=folder_key))
    return render_template('document_form.html', store=store, folder_key=folder_key)


@documents_bp.route('/loja/<store_id>/nova-pasta', methods=['POST'])
@login_required
@admin_required
def create_folder(store_id):
    name = request.form.get('name')
    parent_id = request.form.get('parent_folder_id') or None
    if name:
        db.session.add(CustomFolder(name=name, store_id=store_id, parent_folder_id=parent_id))
        db.session.commit()
        flash('Pasta criada!', 'success')
    return redirect(url_for('documents.folders_grid', store_id=store_id))
