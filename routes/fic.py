from flask import Blueprint, render_template, request, redirect, url_for, session
from models.table_user import db, User
from pprint import pprint #permite mostrar datos complejos de forma facil de leer en consola
import yfinance as yf
rout_fic = Blueprint('fic', __name__)

@rout_fic.route('/simulator', methods=['GET', 'POST'])
def fic_simulador():
    if request.method == 'POST':
        capital_inicial = float(request.form['capital_inicial'])
        aporte_mensual = float(request.form['aporte_mensual'])
        tasa_interes = float(request.form['tasa_interes'])
        años = int(request.form['años'])
        cedear_selec = request.form.get('cedear')
        
        # total de meses de aporte para que simule el bucle mes a mes
        total_meses = años * 12
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
                accion = yf.Ticker(cedear_selec)
                
                # 5 años (period="5y") promedio
                historia = accion.history(period="5y")
                
                if not historia.empty:
                    precio_inicio = historia['Close'].iloc[0]
                    precio_fin = historia['Close'].iloc[-1]
                    
                    #años exactos que pasaron 
                    dias_totales = (historia.index[-1] - historia.index[0]).days
                    años_reales = dias_totales / 365.25
                    
                    if años_reales > 0:
                        # FÓRMULA CAGR (Tasa de Crecimiento Anual Compuesto)
                        # promedio real de crecimiento anual
                        cagr = ((precio_fin / precio_inicio) ** (1 / años_reales)) - 1
                        
                        tasa_anual_cedear = cagr * 100
                        
                        # Pasamos tasa anual promedio a mensual para el bucle
                        tasa_mensual_cedear = (tasa_anual_cedear / 100) / 12
            except:
                tasa_anual_cedear = 0
                tasa_mensual_cedear = 0
        
        
        # se repite la cantidad total de meses de aporte que haga el usuario
        for x in range(total_meses):
            #la ganancia se calcula con el saldo actual * la tasa mensual
            ganancia = saldo_actual * tasa_mensual
            #sumamos la ganancia al saldo actual (el rendimiento del aporte)
            saldo_actual = saldo_actual + ganancia
            #sumamos lo que aporta el usuario por mes
            saldo_actual = saldo_actual + aporte_mensual
            #guardamos el saldo final de cada mes (ganancia + aporte)
            aporte_list.append(saldo_actual)
            
            #si elige cedear
            if cedear_selec:
                ganancia_cedear = saldo_cedear * tasa_mensual_cedear
                saldo_cedear = saldo_cedear + ganancia_cedear
                saldo_cedear = saldo_cedear + aporte_mensual
                lista_cedear.append(saldo_cedear)
            
        userName = session.get('userName') # Recuperamos nombre para no perderlo
        return render_template('dashboard.html', 
            user=userName, 
            total=saldo_actual, 
            #gráfico
            grafico_fic=aporte_list,       
            grafico_cedear=lista_cedear,   
            # Datos para rellenar inputs
            cap_ini=capital_inicial, 
            aporte=aporte_mensual, 
            tasa=tasa_interes,
            años=años, 
            
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