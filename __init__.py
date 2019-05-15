import os
import logging
from flask import Flask, redirect, url_for, session
from database import db_session, init_db

UPLOAD_FOLDER = "static/image/profile/"

# Factory method to create the flask app
def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Register the database with the app
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()
    # Initalize the datebase
    init_db()
    # Redirect to the first page which is the login page
    @app.route('/')
    def start():
        return redirect(url_for('auth.home', index = 0))

    # Register the flask app's blueprints
    import auth
    import admin
    import manager
    import canvasser
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(manager.bp)
    app.register_blueprint(canvasser.bp)
    app.register_blueprint(admin.bp)
    
    logging.debug("blue prints are created for auth, mananger, canvasser, admin")
    
    return app
    

# for testing purposes
# if __name__ == "__main__":
#     app = create_app()
#     app.run()
