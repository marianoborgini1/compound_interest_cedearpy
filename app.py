from flask import Flask
from models.database import db  
from models.table_user import User
from models.table_simulacion import Simulacion
#importacion de rutas
from routes.auth import rout_auth


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = "key_security_pass_dashboard"

#conexion inicializamos y le decimos a la db que esta es nuestra app 
db.init_app(app)

#creamos tabla si no existe el archivo db
with app.app_context():
    db.create_all()

#registro de rutas 
app.register_blueprint(rout_auth)

if __name__ == "__main__":
    app.run(debug=True)