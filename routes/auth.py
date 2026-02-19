from flask import Blueprint, render_template, request, redirect, url_for, session
from models.table_user import db, User
from pprint import pprint #permite mostrar datos complejos de forma facil de leer en consola

rout_auth = Blueprint('auth', __name__)

@rout_auth.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    
    # si el userId no esta en la sesion vuelve a login, nadie puede entrar dashboard a menos que haya iniciado sesion o que tenga sus datos guardados en la memoria del navegador 
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
            
            # si el usuario ingresa los datos correctamente, se le guarda el user y el id en la memoria del navegador para que dashboard entienda quien esta en la sesion
            session['userId'] = userFound.id
            session['userName'] = userFound.user
            return redirect(url_for('auth.dashboard'))
        else:
            return "ERROR. El email o la contraseña son incorrectos. Intenta nuevamente."
    else:
        return render_template('login.html')

@rout_auth.route('/register', methods= ['GET', 'POST'])
def register():
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
    
        # se arma la sesión automáticamente al registrarse, manda id y user a la memoria de la web para saber quien esta en la sesion
        session['userId'] = newUser.id
        session['userName'] = newUser.user
        
        #redirige a la pagina de inicia si todo es correcto
        return redirect(url_for('auth.dashboard'))
        
    else:
        return render_template('register.html')

@rout_auth.route('/logout')
def logout():
    # si el usuario oprime [cerrar sesion] vuelve a login
    session.clear()
    return redirect(url_for('auth.login'))