from models.database import db

class Simulacion(db.Model):
    __tablename__ = 'Simulacion'
    id = db.Column(db.Integer, primary_key = True)
    
    # Conexion con el usuario dueño
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    capital_inicial = db.Column(db.Integer, nullable=False)
    aporte_mensual = db.Column(db.Integer, nullable=False)
    anios = db.Column(db.Integer, nullable=False)
    tasa_manual = db.Column(db.Float, nullable=False)
    activo_elegido = db.Column(db.String(50), nullable=True)
    total_fijo = db.Column(db.Float, nullable=True)
    total_cedear = db.Column(db.Float, nullable=True)
    tasa_cedear = db.Column(db.Float, nullable=True)