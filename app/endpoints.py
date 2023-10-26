import os
import stat
from flask import jsonify, request, send_file
from http import HTTPStatus

from app.utils import (
    get_unique_filename,
    get_file_name,
    find_file,
    check_user_auth,
    check_user_is_author
)
from app import UPLOAD_FOLDER, app, db


@app.route('/', methods=['POST',])
def upload_file():
    db_user = check_user_auth(request)
    file = request.files['file']
    filename_hash = get_unique_filename()
    dir_name = filename_hash[:2]
    try:
        upload_folder = UPLOAD_FOLDER + dir_name
        file_name = get_file_name(filename_hash, file)
        file.save(os.path.join(upload_folder, file_name))
    except Exception:
        new_folder = os.path.join(
            UPLOAD_FOLDER,
            dir_name
            )
        os.mkdir(new_folder)
        file_name = get_file_name(filename_hash, file)
        file.save(os.path.join(new_folder, file_name))
    user_files = db_user.user_files
    if user_files is None:
        db_user.user_files = filename_hash + ','
    else:
        db_user.user_files += filename_hash + ','
    db.session.add(db_user)
    db.session.commit()

    return jsonify({
        'status': HTTPStatus.CREATED,
        'hashed_name': filename_hash
        })


@app.route('/<string:hash_file_name>/', methods=['GET',])
def download_file(hash_file_name: str):
    file_path, file_list = find_file(hash_file_name)
    return send_file(file_path)


@app.route('/<string:hash_file_name>/', methods=['DELETE',])
def delete_file(hash_file_name: str):
    db_user = check_user_auth(request)
    check_user_is_author(db_user, hash_file_name)
    file_path, file_list = find_file(hash_file_name)
    if len(file_list) > 1:
        os.remove(file_path)
    else:
        os.chmod(file_path, stat.S_IWRITE)
        os.remove(file_path)
        dir_path = file_path.split('.')[0].replace(hash_file_name, '')
        os.rmdir(dir_path)
    db_user.user_files = db_user.user_files.replace(f'{hash_file_name},', '')
    db.session.add(db_user)
    db.session.commit()
    return jsonify({
        'status': HTTPStatus.NO_CONTENT,
        'messege': 'File deleted'
        })
