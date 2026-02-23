from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.table_user import db, User
from models.table_simulacion import Simulacion
from pprint import pprint #Permite mostrar datos complejos de forma facil de leer en consola
#Libreria para obtener datos de los cedear
import os
import yfinance as yf
import requests # Agregado para configurar el proxy en PythonAnywhere

rout_fic = Blueprint('fic', __name__)

@rout_fic.route('/simulator', methods=['GET', 'POST'])
def fic_simulador():
    if request.method == 'POST':
        capital_inicial = float(request.form['capital_inicial'])
        aporte_mensual = float(request.form['aporte_mensual'])
        tasa_interes = float(request.form['tasa_interes'])
        anios = int(request.form['anios'])
        cedear_selec = request.form.get('cedear')
        
        # total de meses de aporte para que simule el bucle mes a mes
        total_meses = anios * 12
        # convertimos la tasa anual en una tasa mensual para calcular cuanto rinde cada aporte
        tasa_mensual = (tasa_interes / 100) / 12
        # el saldo actual del usuario va a ser el capital con el que inicia 
        saldo_actual = capital_inicial
        # creamos una lista donde te guardan los aportes para crear un grafico
        aporte_list = []
        
        # si elige cedear
        saldo_cedear = capital_inicial
        lista_cedear = []
        tasa_anual_cedear = 0      # Para guardar el % real que traiga la API
        tasa_mensual_cedear = 0    # Para usar en el bucle
        
        # Si usuario eligió un CEDEAR
        if cedear_selec:
            try:
                # Detectamos automáticamente si estamos en la compu o en PythonAnywhere
                if 'PYTHONANYWHERE_DOMAIN' in os.environ:
                    # Estamos en la nube: usamos el proxy
                    proxy = "http://proxy.server:3128"
                    sesion_proxy = requests.Session()
                    sesion_proxy.proxies = {'http': proxy, 'https': proxy}
                    accion_yf = yf.Ticker(cedear_selec, session=sesion_proxy)
                else:
                    # Estamos en tu PC local: funcionamos normal sin proxy
                    accion_yf = yf.Ticker(cedear_selec)
                
                # toma periodo de 5 años (period="5y") promedio
                historia = accion_yf.history(period="5y")
                
                if not historia.empty:
                    precio_inicio = historia['Close'].iloc[0]
                    precio_fin = historia['Close'].iloc[-1]
                    
                    # Años exactos que pasaron 
                    dias_totales = (historia.index[-1] - historia.index[0]).days
                    anios_reales = dias_totales / 365.25
                    
                    if anios_reales > 0:
                        # FÓRMULA CAGR (Tasa de Crecimiento Anual Compuesto)
                        cagr = ((precio_fin / precio_inicio) ** (1 / anios_reales)) - 1
                        tasa_anual_cedear = cagr * 100
                        
                        # Pasamos tasa anual a promedio a mensual para el bucle
                        tasa_mensual_cedear = (tasa_anual_cedear / 100) / 12
            except:
                tasa_anual_cedear = 0
                tasa_mensual_cedear = 0
        
        # Se repite la cantidad total de meses de aporte que haga el usuario
        for x in range(total_meses):
            # La ganancia se calcula con el saldo actual * la tasa mensual
            ganancia = saldo_actual * tasa_mensual
            # Sumamos la ganancia al saldo actual (el rendimiento del aporte)
            saldo_actual = saldo_actual + ganancia
            # Sumamos lo que aporta el usuario por mes
            saldo_actual = saldo_actual + aporte_mensual
            # Guardamos el saldo final de cada mes (ganancia + aporte)
            aporte_list.append(saldo_actual)
            
            # Si elige cedear
            if cedear_selec:
                ganancia_cedear = saldo_cedear * tasa_mensual_cedear
                saldo_cedear = saldo_cedear + ganancia_cedear
                saldo_cedear = saldo_cedear + aporte_mensual
                lista_cedear.append(saldo_cedear)
            
        # Nombre y ID guradados en navegador
        userName = session.get('userName')
        user_id = session.get('userId')
        
        # Guardar en db
        accion = request.form.get('accion') 
        
        if accion == 'guardar':
            # Nuevo registro en la tabla Simulacion (ahora con los totales forzados a float de Python)
            nueva_simulacion = Simulacion(
                id_user=user_id,
                capital_inicial=float(capital_inicial),
                aporte_mensual=float(aporte_mensual),
                anios=int(anios),
                activo_elegido=cedear_selec if cedear_selec else 'Personalizado',
                tasa_manual=float(tasa_interes),
                total_fijo=float(saldo_actual),
                total_cedear=float(saldo_cedear) if cedear_selec else 0.0,
                tasa_cedear=float(tasa_anual_cedear) if cedear_selec else 0.0
            )
            db.session.add(nueva_simulacion)
            db.session.commit()
            
            flash('¡Simulación guardada en tu historial con éxito!', 'success')
            
        return render_template('dashboard.html', 
            user=userName, 
            total=saldo_actual, 
            # Gráfico
            grafico_fic=aporte_list,       
            grafico_cedear=lista_cedear,   
            # Datos para rellenar inputs
            cap_ini=capital_inicial, 
            aporte=aporte_mensual, 
            tasa=tasa_interes,
            anios=anios, 
            
            # Datos del CEDEAR
            nombre_cedear=cedear_selec,
            total_cedear=saldo_cedear,
            tasa_cedear_real=round(tasa_anual_cedear, 2)
            )
    else:
        if 'userId' not in session:
            return redirect(url_for('auth.login'))
        
        userName = session.get('userName')
        return render_template('dashboard.html', user=userName)

@rout_fic.route('/mis-simulaciones')
def mis_simulaciones():
    if 'userId' not in session:
        return redirect(url_for('auth.login'))
        
    user_id = session.get('userId')
    userName = session.get('userName')
    
    # Buscam todas las simulaciones del usuario específico
    # Orden por ID de mayor a menor 
    simulaciones = Simulacion.query.filter_by(id_user=user_id).order_by(Simulacion.id.desc()).all()
    
    return render_template('record.html', user=userName, simulaciones=simulaciones)

@rout_fic.route('/borrar-simulacion/<int:id>', methods=['POST'])
def delete_simulacion(id):
    # Verificamos que el usuario haya iniciado sesión
    if 'userId' not in session:
        return redirect(url_for('auth.login'))
    
    # Buscamos la simulación por ID
    sim = Simulacion.query.get(id)
    
    # Seguridad: solo la borra si existe y si el id_user coincide con el usuario actual
    if sim and sim.id_user == session['userId']:
        db.session.delete(sim)
        db.session.commit()
        flash('Simulación eliminada correctamente.', 'success')
        
    return redirect(url_for('fic.mis_simulaciones'))