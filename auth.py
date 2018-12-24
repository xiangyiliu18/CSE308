import os
import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app)
from werkzeug.security import check_password_hash, generate_password_hash
from database import db_session, User, init_db, Role, GlobalVariables
from werkzeug.utils import secure_filename
from admin import allowed_file, unique_user, ALLOWED_EXTENSIONS

# Create blueprint for auth
bp = Blueprint('auth', __name__, url_prefix='/auth')

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#If duplicate the user, then return True, else--> False
def dup_user(test_email):
    user = User.query.filter(User.email == test_email).first()
    if user is None:
        return False
    else:
        return True

@bp.route('/home/<index>')
def home(index):
    return render_template('home.html',index = index)

@bp.route("/home/signup",  methods=('GET', 'POST'))
def signup():
    error = None
    if request.method == 'POST': 
        file = None
        filename = None
        if 'file' in request.files:
            file = request.files['file']
        name = request.form['name']
        email = request.form['email']
        password = (request.form['password'])
        confirm_password = (request.form['confirm-password'])
        manager = request.form.get('toggle-manager')
        canvasser = request.form.get('toggle-canvasser')
        # ALready catched all fields, then check it!!!!
        if dup_user(email):
            flash("The user already exists, please create new account!")
            return redirect(url_for('auth.home',index = 1))
        if (password != confirm_password):
            flash("Please match the password before signup!")
            return redirect(url_for('auth.home',index = 1))
        if not(manager == 'yes' or canvasser == 'yes'):
            flash("Please select at least one account type!")
            return redirect(url_for('auth.home',index = 1))
        #Everthing is valid.  Create this user to DB
        if file and file.filename != '' and allowed_file(file.filename):
            app = current_app._get_current_object()
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        ps = generate_password_hash(password)
        new_user = User(email,ps,name,filename)
        db_session.add(new_user)
        db_session.commit()
        if manager == 'yes':
            role = Role('manager')
            new_user.users_relation.append(role)
        if canvasser == 'yes':
            role = Role('canvasser')
            new_user.users_relation.append(role)
        db_session.commit() 
        flash("Create one new account Successfully!!")
    return redirect(url_for('auth.home',index = 0))

@bp.route('/home/login',  methods=('GET', 'POST'))
def login():
    error = None
    if ('remember' not in session):
        session.clear()
    if request.method == 'POST':
        session.clear()
        info={}  # THe dict to store all user info
        choice = request.form.get('toggle')  # Get user login account type: admin is the default choice
        email = request.form['login-email']
        password = request.form['login-password']
        remember= request.form.get('remember-me')
        if email and password and choice:  # No empty fields
            user = User.query.filter(User.email == email).first()  # Get User object
            if user is None:
                flash("Error! This user does not exist, please enter the correct one!")
                return redirect(url_for('auth.home',index = 2))
            role_table = user.users_relation  # Get role objects related to this user
            roles=[]  # For storing roles of this login user
            if role_table is None :
                flash("This user does not exist, please enter the correct one!")
                return redirect(url_for('auth.home',index = 2))
            ################ Get Role Obejects For Login User
            for ele in role_table:
                roles.append(ele.role)  ########## eg: roles=[canvasser, admin, manager]
            ########### Check if the choice exists in roles
            if choice not in roles:
                flash("This user does not exist, please enter the correct one!")
                return redirect(url_for('auth.home',index = 2))
            ############# Check passwords #################
            if(not check_password_hash(user.password, password)):
                flash("Incorrect password. Please enter the correct one !")
                return redirect(url_for('auth.home',index = 2))
            #Add user info to the session
            info['email'] = email
            info['password'] = password
            info['name'] = user.name
            info['roles']= roles
            info['role'] = choice   ############# Login Acccout Type
            info['account'] = choice  ############# For Backing to Homepage when manipulating profile
            info['avatar'] = user.avatar    ############# Store User's avatar image file

            session['info'] = info  ############ Store all logging user's info
            ##################### Work on 'Remember Me session' ########################
            if remember:
                session['remember'] = True
            ##################### Query Global Parameters ###################
            params_table = GlobalVariables.query.first()
            session['params'] = [params_table.workDayLength, params_table.averageSpeed]  ## minutes ; miles/minutes
            if choice == 'admin':
                return redirect(url_for('admin.adminPage',u_name = session['info']['name']))
            elif(choice == 'manager'):
                return redirect(url_for('manager.manPage',u_name=user.name))
            elif(choice == 'canvasser'):
                return redirect(url_for('canvasser.canPage',u_name=user.name))
    return redirect(url_for('auth.home',index = 2))


@bp.route("/logout")
def logout():
    if not ('remember' in session):
        session.clear()
    return redirect(url_for('auth.home',index = 0))


@bp.route("/profile/<u_email>", methods=('GET', 'POST'))
def profile(u_email):
    result = None
    file = None
    filename = session['info']['avatar']

    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        if 'file' in request.files:
            file = request.files['file']
        if password != confirm_password:
            result = "Error, Passwords do not match, please enter comfirm your password!!"
            return render_template('profile.html', u_email= u_email, result = result)
        if not unique_user(u_email, email):
            result = 'Error, This email already is used, please change to other one or just keep the origin!!!'
            return render_template('profile.html', u_email= u_email, result = result)
        app = current_app._get_current_object()
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # All info are valid
        user = User.query.filter(User.email == u_email).first()
        commit = False
        if name != user.name :
            commit = True
            user.name = name
            session['info']['name'] = name
        if email != user.email:
            commit = True
            user.email = email
            session['info']['email'] = email
        if not check_password_hash(user.password, password):
            commit = True
            ps = generate_password_hash(password)
            user.password = ps
            session['info']['password'] = password
        if (filename is not None) and (filename != session['info']['avatar']):
            user.avatar = filename
            session['info']['avatar'] = filename
            commit = True
        if commit:
            db_session.commit()
            result = "Saved Successfully"
        else:
            result ="Nothing Changes !! "
        ## if not set, Flask  will not send the updated session cookis to the client
        session.modified = True

    return render_template('profile.html', u_email = u_email, result = result)

@bp.route("/profile/homepage")
def back():
    if session:
        if session['info']['account'] == 'admin':
            return redirect(url_for('admin.adminPage',u_name = session['info']['name']))
        elif(session['info']['account'] == 'manager'):
            return redirect(url_for('manager.manPage',u_name=session['info']['name']))
        elif(session['info']['account'] == 'canvasser'):
            return redirect(url_for('canvasser.canPage',u_name=session['info']['name']))

    return redirect(url_for('auth.home',index = 0))



