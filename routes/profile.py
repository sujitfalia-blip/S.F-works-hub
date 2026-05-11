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


profile_bp = Blueprint("profile", __name__)


# ================= MY PROFILE =================
@profile_bp.route('/profile')
def my_profile():

    # LOGIN CHECK
    if 'user_id' not in session:
        return redirect('/auth/login')

    user = db.session.get(
        User,
        session['user_id']
    )

    if not user:
        return redirect('/auth/login')

    # GET PROFILE
    profile = Profile.query.filter_by(
        user_id=user.id
    ).first()

    # GALLERY
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

    viewed_user = User.query.get(user_id)

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

    # LOGIN CHECK
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

    # CREATE PROFILE
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

    # ================= SAVE FORM =================

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

        filename = secure_filename(
            profile_img.filename
        )

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

        filename = secure_filename(
            cover_img.filename
        )

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

            filename = secure_filename(
                file.filename
            )

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
    
