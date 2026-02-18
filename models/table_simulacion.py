from models.database import db

class Simulacion(db.Model):
    __tablename__ = 'Simulacion'
    id = db.Column(db.Integer, primary_key = True)
    
    # La conexion con el usuario dueño
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    capital_inicial = db.Column(db.Integer, nullable=False)
    aporte_mensual = db.Column(db.Integer, nullable=False)
    anios = db.Column(db.Integer, nullable=False)
    activo_elegido = db.Column(db.String(50), nullable=True)
    tasa_manual = db.Column(db.Float, nullable=True)
    