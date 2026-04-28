import os
from dotenv import load_dotenv

# Carga las variables ANTES de importar otras cosas
load_dotenv()

from flask import Flask, session, url_for, render_template, redirect
from models.database import db  
from models.table_user import User
from models.table_simulacion import Simulacion

# Importacion de rutas
from routes.auth import rout_auth
from routes.fic import rout_fic

app = Flask(__name__)

# Llama a la URL de la base de datos desde el .env por seguridad
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Llama a la clave desde el .env 
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_key_flask')

app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USER')

# Conexion inicializamos y le decimos a la db que esta es nuestra app 
db.init_app(app)

# Creamos tabla si no existe el archivo db
with app.app_context():
    db.create_all()

# Registro de rutas 
app.register_blueprint(rout_auth)
app.register_blueprint(rout_fic)

@app.route('/')
def index():
    # Si tiene sesión iniciada redirige al dashboard
    if 'userId' in session:
        return redirect(url_for('auth.dashboard'))
        
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)