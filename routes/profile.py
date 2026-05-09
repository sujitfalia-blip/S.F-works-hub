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


profile = Blueprint(
    'profile',
    __name__
)



# ================= PROFILE SETUP =================
@profile.route('/profile/setup', methods=['GET', 'POST'])
def profile_setup():

    if 'user_id' not in session:
        return redirect('/login')

    user = User.query.get(session['user_id'])

    # ================= GET PAGE =================
    if request.method == 'GET':

        profile_data = Profile.query.filter_by(
            user_id=user.id
        ).first()

        return render_template(
            'user/profile_setup.html',
            user=user,
            profile=profile_data
        )



    # ================= CHECK PROFILE =================
    profile_data = Profile.query.filter_by(
        user_id=user.id
    ).first()

    if not profile_data:

        profile_data = Profile(
            user_id=user.id
        )

        db.session.add(profile_data)



    # ================= BASIC INFO =================
    profile_data.name = request.form.get('name')

    profile_data.address = request.form.get('address')

    profile_data.age = request.form.get('age')

    profile_data.education = request.form.get('education')

    profile_data.area = request.form.get('area')

    profile_data.gender = request.form.get('gender')

    profile_data.religion = request.form.get('religion')

    profile_data.country = request.form.get('country')

    profile_data.work_desc = request.form.get('work_desc')



    # ================= PROFILE IMAGE =================
    profile_img = request.files.get('profile_img')

    if profile_img and profile_img.filename != '':

        filename = secure_filename(profile_img.filename)

        path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            filename
        )

        profile_img.save(path)

        profile_data.profile_img = f"uploads/{filename}"



    # ================= COVER IMAGE =================
    cover_img = request.files.get('cover_img')

    if cover_img and cover_img.filename != '':

        filename = secure_filename(cover_img.filename)

        path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            filename
        )

        cover_img.save(path)

        profile_data.cover_img = f"uploads/{filename}"



    # ================= GALLERY =================
    gallery_files = request.files.getlist('gallery')

    gallery_paths = []

    for file in gallery_files:

        if file and file.filename != '':

            filename = secure_filename(file.filename)

            path = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                filename
            )

            file.save(path)

            gallery_paths.append(
                f"uploads/{filename}"
            )



    if gallery_paths:

        profile_data.gallery = json.dumps(
            gallery_paths
        )



    # ================= SAVE =================
    db.session.commit()

    return redirect('/user/dashboard')
