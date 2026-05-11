from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    current_app
)

from werkzeug.utils import secure_filename

from models.profile import Profile
from models.user import User

from extensions import db

import os
import json
import uuid


profile_bp = Blueprint("profile", __name__)


# ================= MY PROFILE =================
@profile_bp.route('/profile')
def my_profile():

    if 'user_id' not in session:
        return redirect('/auth/login')

    user = db.session.get(
        User,
        session['user_id']
    )

    if not user:
        return redirect('/auth/login')

    profile = Profile.query.filter_by(
        user_id=user.id
    ).first()

    gallery = []

    if profile and profile.gallery:

        try:
            gallery = json.loads(profile.gallery)
        except:
            gallery = []

    return render_template(
        "profile.html",
        user=user,
        profile=profile,
        gallery=gallery
    )


# ================= VIEW OTHER PROFILE =================
@profile_bp.route('/profile/<int:user_id>')
def view_profile(user_id):

    profile = Profile.query.filter_by(
        user_id=user_id
    ).first()

    viewed_user = db.session.get(
        User,
        user_id
    )

    if not profile:
        return "Profile not found"

    gallery = []

    if profile.gallery:

        try:
            gallery = json.loads(profile.gallery)
        except:
            gallery = []

    return render_template(
        "profile.html",
        user=viewed_user,
        profile=profile,
        gallery=gallery
    )


# ================= PROFILE SETUP =================
@profile_bp.route('/profile/setup', methods=['GET', 'POST'])
def profile_setup():

    if 'user_id' not in session:
        return redirect('/auth/login')

    user = db.session.get(
        User,
        session['user_id']
    )

    if not user:
        return redirect('/auth/login')

    # FIND PROFILE
    profile = Profile.query.filter_by(
        user_id=user.id
    ).first()

    # CREATE PROFILE IF NOT EXISTS
    if not profile:

        profile = Profile(
            user_id=user.id
        )

        db.session.add(profile)
        db.session.commit()

    # ================= GET REQUEST =================
    if request.method == 'GET':

        gallery = []

        if profile.gallery:

            try:
                gallery = json.loads(profile.gallery)
            except:
                gallery = []

        return render_template(
            "edit_profile.html",
            user=user,
            profile=profile,
            gallery=gallery
        )

    # ================= POST REQUEST =================
    try:

        profile.name = request.form.get(
            'name',
            ''
        )

        profile.address = request.form.get(
            'address',
            ''
        )

        age = request.form.get('age')

        if age and age.isdigit():
            profile.age = int(age)

        profile.education = request.form.get(
            'education',
            ''
        )

        profile.area = request.form.get(
            'area',
            ''
        )

        profile.gender = request.form.get(
            'gender',
            ''
        )

        profile.religion = request.form.get(
            'religion',
            ''
        )

        profile.country = request.form.get(
            'country',
            ''
        )

        profile.work_desc = request.form.get(
            'work_desc',
            ''
        )

    except Exception as e:
        return f"Form Error: {e}"

    # ================= UPLOAD FOLDER =================

    upload_folder = current_app.config[
        'UPLOAD_FOLDER'
    ]

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    # ================= PROFILE IMAGE =================

    profile_img = request.files.get(
        'profile_img'
    )

    if profile_img and profile_img.filename != '':

        ext = profile_img.filename.rsplit('.', 1)[1].lower()

        filename = f"{uuid.uuid4()}.{ext}"

        filepath = os.path.join(
            upload_folder,
            filename
        )

        profile_img.save(filepath)

        profile.profile_img = (
            f"static/uploads/{filename}"
        )

    # ================= COVER IMAGE =================

    cover_img = request.files.get(
        'cover_img'
    )

    if cover_img and cover_img.filename != '':

        ext = cover_img.filename.rsplit('.', 1)[1].lower()

        filename = f"{uuid.uuid4()}.{ext}"

        filepath = os.path.join(
            upload_folder,
            filename
        )

        cover_img.save(filepath)

        profile.cover_img = (
            f"static/uploads/{filename}"
        )

    # ================= GALLERY =================

    gallery_files = request.files.getlist(
        'gallery'
    )

    gallery_list = []

    # OLD GALLERY
    if profile.gallery:

        try:
            gallery_list = json.loads(
                profile.gallery
            )
        except:
            gallery_list = []

    # NEW GALLERY
    for file in gallery_files:

        if file and file.filename != '':

            ext = file.filename.rsplit('.', 1)[1].lower()

            filename = f"{uuid.uuid4()}.{ext}"

            filepath = os.path.join(
                upload_folder,
                filename
            )

            file.save(filepath)

            gallery_list.append(
                f"static/uploads/{filename}"
            )

    profile.gallery = json.dumps(
        gallery_list
    )

    # ================= SAVE DATABASE =================

    try:

        db.session.commit()

    except Exception as e:

        db.session.rollback()

        return f"Database Error: {e}"

    return redirect('/profile')


# ================= DELETE GALLERY IMAGE =================
@profile_bp.route('/delete-gallery-image/<int:index>')
def delete_gallery_image(index):

    if 'user_id' not in session:
        return redirect('/auth/login')

    profile = Profile.query.filter_by(
        user_id=session['user_id']
    ).first()

    if not profile:
        return redirect('/profile')

    gallery = []

    if profile.gallery:

        try:
            gallery = json.loads(profile.gallery)
        except:
            gallery = []

    # DELETE IMAGE
    if 0 <= index < len(gallery):

        img_path = gallery[index]

        full_path = os.path.join(
            current_app.root_path,
            img_path
        )

        # DELETE FILE
        if os.path.exists(full_path):

            try:
                os.remove(full_path)
            except:
                pass

        # REMOVE FROM GALLERY
        gallery.pop(index)

        profile.gallery = json.dumps(
            gallery
        )

        db.session.commit()

    return redirect('/profile')
