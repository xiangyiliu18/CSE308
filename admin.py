from flask import (Blueprint, flash, g, redirect, render_template, request, url_for, session, current_app)
from werkzeug.exceptions import abort
from database import db_session, User, GlobalVariables, Role
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os

# Create the admin blueprint
bp = Blueprint('admin', __name__, url_prefix='/admin')

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def unique_user(old_email, new_email):
    if old_email!= new_email:
        new_user = User.query.filter(User.email == new_email).first()
        if new_user is not None:
            return False
    return True

# Function to render the admin page and set the admin page url
@bp.route('/adminPage/<u_name>/', methods=('GET', 'POST'))
def adminPage(u_name):
    if 'info' not in session:
        ############## Need Login Firstly, it seldom happens
        return redirect(url_for('auth.home',index = 1))
    ################# After logging, retrieve all data fro user interface###################
    user_table = db_session.query(User).order_by(User.email).filter(User.email != session['info']['email'])
    # Dic to store other users info: Key = email ; Value = all info of this email(name, avatar, roles)
    users={}
    session['info']['account'] = 'admin'
    ## if not set, Flask  will not send the updated session cookis to the client
    session.modified = True

    ############### Retrieve all data for each user ######################
    for ele in user_table:
        instance={}
        instance['name'] = ele.name
        instance['avatar'] = ele.avatar
        instance['roles']=[]
        for role_ele in ele.users_relation:
            instance['roles'].append(role_ele.role)
        users[ele.email]= instance
    ################ Work For Changing GLoabl Parameters############################
    if request.method == 'POST':  
        workday = int(request.form['workday'])##### Integer in minutes
        movspeed = float(request.form['movspeed'])  ############ Interger in miles/minutes
        params = GlobalVariables.query.first()
        commmit = False
        if workday != session['params'][0]:         ######### Store it to DB in minutes
            session['params'][0] = workday
            commmit = True
            params.workDayLength = workday

        if movspeed != session['params'][1]:
            commmit = True
            session['params'][1] = movspeed
            params.averageSpeed = movspeed

        ############### If changes made, commit it to DB ###########################
        if commmit:
            db_session.commit()
    ################## For keeping all users info into Session
    session['users'] = users
    return render_template('admin_html/admin.html')


# Function that handles deleting users
@bp.route('/delete/<u_email>/', methods=('GET', 'POST'))
def delete(u_email):
    if request.method == 'POST':
        deletedUser = User.query.filter(User.email == u_email).first()
        if deletedUser is not None:
            db_session.delete(deletedUser)
            db_session.commit() 
            flash("Delete Successfully","info")
    return redirect(url_for('admin.adminPage',u_name=session['info']['name']))
        
# Function for handling adding
@bp.route('/add', methods=('GET', 'POST'))
def add():
    file = None
    filename = None
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        if 'file' in request.files:
            file = request.files['file']
        admin = request.form.get('admin')
        manager = request.form.get('manager')
        canvasser = request.form.get('canvasser')
        if not (admin == "admin" or manager == "manager" or canvasser == "canvasser"):
            flash("Fail to add, You must set at least one position for this user!!", "error")
            return redirect(url_for("admin.adminPage", u_name = session['info']['name']))
        if password != confirm_password:
            flash("Fail to add, Please Match password!!", "error")
            return redirect(url_for("admin.adminPage", u_name = session['info']['name']))
        if not unique_user(session['info']['email'], email):
            flash("Fail to add, This email already is used!!")
            return redirect(url_for("admin.adminPage", u_name = session['info']['name']))
        user = User.query.filter(User.email == email).first()
        if user is not None:
            flash("Fail to add, This email already exists, please add another one", "error")
            return redirect(url_for("admin.adminPage", u_name = session['info']['name']))
        else:  # Everything already matches
            if file and file.filename != '' and allowed_file(file.filename):
                app = current_app._get_current_object()
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ps = generate_password_hash(password)
            new_user = User(email,ps, name, filename)
            db_session.add(new_user)
            db_session.commit()
            if admin == "admin":
                role = Role('admin')
                new_user.users_relation.append(role)
            if canvasser == "canvasser":
                role = Role('canvasser')
                new_user.users_relation.append(role)
            if manager == "manager":
                role = Role('manager')
                new_user.users_relation.append(role)
            db_session.commit()
            flash("add user Successfully", "info")
    return redirect(url_for('admin.adminPage', u_name = session['info']['name']))

#  Function that handles editing users
@bp.route('/edit/<u_email>', methods=('GET', 'POST'))
def edit(u_email):
    file = None
    filename = None
    if request.method == "POST":
        user = User.query.filter(User.email == u_email).first()
        print(user)
        filename = user.avatar
        name = request.form['name']
        email = request.form['email']
        admin = request.form.get('admin')
        manager = request.form.get('manager')
        canvasser = request.form.get('canvasser')
        if 'file' in request.files:
            file = request.files['file']
        if not (admin == "admin" or manager == "manager" or canvasser == "canvasser"):
            flash("Fail to edit, You must set at least one position for this user!!", "error")
            return redirect(url_for("admin.adminPage", u_name = session['info']['name']))
        if not unique_user(u_email, email):
            flash("Fail to edit, This email already is used!!", "error")
            return redirect(url_for("admin.adminPage", u_name = session['info']['name']))
        if file and file.filename != ''and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            app = current_app._get_current_object()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Match everthing
        user.name = name
        user.email = email
        user.avatar = filename
        db_session.commit()
        role_relation = user.users_relation
        roles = []
        others = []
        if admin == "admin":
            others.append(admin)
        if manager == "manager":
            others.append(manager)
        if canvasser == "canvasser":
            others.append(canvasser)
        for ele in role_relation:
            if ele.role not in others:
                user.users_relation.remove(ele)
            else:
                roles.append(ele.role)
        for ele in others:
            if ele not in roles:
                role = Role(ele)
                user.users_relation.append(role)
        db_session.commit()
        flash("Saved Successfully","info")
    return redirect(url_for('admin.adminPage', u_name = session['info']['name']))
