from flask import Blueprint, render_template, request, redirect, url_for, session
from models.table_user import db, User
from pprint import pprint #permite mostrar datos complejos de forma facil de leer en consola

rout_auth = Blueprint('auth', __name__)

@rout_auth.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'userId' not in session:
        return redirect(url_for('auth.login'))
    
    userName = session.get('userName')
    return render_template('dashboard.html', user=userName)
        
@rout_auth.route('/login', methods= ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # 2. Buscamos en la tabla User si hay alguien con ese email
        # El .first() es para que nos devuelva un objeto con atributos y no una lista
        userFound = User.query.filter_by(email=email).first()
        
        if userFound and userFound.password == password:
            
            session['userId'] = userFound.id
            session['userName'] = userFound.user
            return redirect(url_for('auth.dashboard'))
        else:
            return "ERROR. El email o la contraseña son incorrectos. Intenta nuevamente."
    else:
        return render_template('login.html')

@rout_auth.route('/registro', methods= ['GET', 'POST'])
def registro():
    if request.method == 'POST':
        
        user = request.form["user"]
        email = request.form["email"]
        password = request.form["password"]
        
        #consulta en la db si el email ingresado existe 
        userExist = User.query.filter_by(email=email).first()
        
        if userExist:
            return "El email ingresado ya esta registrado. Ingrese otro email o inicie sesion."
        
        newUser = User(user=user, email=email, password=password)
        
        db.session.add(newUser)
        db.session.commit()
        
        pprint(request.form)
        #redirige a la pagina de inicia si todo es correcto
        #return redirect(url_for('dashboard.html'))
        return "¡Usuario guardado con éxito en la base de datos!"
        
    else:
        return render_template('registro.html')

@rout_auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))