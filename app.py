from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
import zipfile
import io
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'condominio-seguro-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///condominio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BASE_URL'] = os.environ.get('BASE_URL', 'http://192.168.22.205:5000')

db = SQLAlchemy(app)


class PlazaEstacionamiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    sector = db.Column(db.String(20), nullable=False)
    __table_args__ = (db.UniqueConstraint('numero', 'sector', name='unique_plaza'),)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), nullable=False)


class Departamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), unique=True, nullable=False)
    piso = db.Column(db.Integer, nullable=False)
    propietario = db.Column(db.String(100), nullable=False)


class Visita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_ingreso = db.Column(db.DateTime, default=datetime.now)
    fecha_salida = db.Column(db.DateTime, nullable=True)
    nombre = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20))
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamento.id'))
    departamento = db.relationship('Departamento')
    motivo = db.Column(db.String(200))
    usuario_registra_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    usuario_registra = db.relationship('User')


class Encomienda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_recepcion = db.Column(db.DateTime, default=datetime.now)
    fecha_retiro = db.Column(db.DateTime, nullable=True)
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamento.id'))
    departamento = db.relationship('Departamento')
    remitente = db.Column(db.String(100))
    descripcion = db.Column(db.String(200))
    quien_retira = db.Column(db.String(100), nullable=True)
    usuario_registra_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    usuario_registra = db.relationship('User')


class Estacionamiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_ingreso = db.Column(db.DateTime, default=datetime.now)
    fecha_salida = db.Column(db.DateTime, nullable=True)
    patente = db.Column(db.String(20), nullable=False)
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamento.id'))
    departamento = db.relationship('Departamento')
    marca = db.Column(db.String(50))
    color = db.Column(db.String(30))
    sector = db.Column(db.String(20), default='Vespucio')
    plaza = db.Column(db.Integer, nullable=True)
    usuario_registra_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    usuario_registra = db.relationship('User')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def rol_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('rol') not in roles:
                flash('No tienes permisos para acceder', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['nombre'] = user.nombre
            session['rol'] = user.rol
            return redirect(url_for('dashboard'))
        flash('Credenciales incorrectas', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    visitas_activas = Visita.query.filter_by(fecha_salida=None).count()
    encomiendas_pendientes = Encomienda.query.filter_by(fecha_retiro=None).count()
    autos_estacionados = Estacionamiento.query.filter_by(fecha_salida=None).count()
    
    plazas_total = PlazaEstacionamiento.query.count()
    plazas_ocupadas = Estacionamiento.query.filter_by(fecha_salida=None).with_entities(Estacionamiento.plaza).filter(Estacionamiento.plaza != None).distinct().count()
    plazas_disponibles = plazas_total - plazas_ocupadas
    
    vespucio_total = PlazaEstacionamiento.query.filter_by(sector='Vespucio').count()
    vespucio_ocupadas = Estacionamiento.query.filter_by(fecha_salida=None, sector='Vespucio').with_entities(Estacionamiento.plaza).filter(Estacionamiento.plaza != None).distinct().count()
    
    av_total = PlazaEstacionamiento.query.filter_by(sector='AV').count()
    av_ocupadas = Estacionamiento.query.filter_by(fecha_salida=None, sector='AV').with_entities(Estacionamiento.plaza).filter(Estacionamiento.plaza != None).distinct().count()
    
    return render_template('dashboard.html', 
                           visitas_activas=visitas_activas,
                           encomiendas_pendientes=encomiendas_pendientes,
                           autos_estacionados=autos_estacionados,
                           plazas_disponibles=plazas_disponibles,
                           vespucio_total=vespucio_total,
                           vespucio_ocupadas=vespucio_ocupadas,
                           av_total=av_total,
                           av_ocupadas=av_ocupadas,
                           now=datetime.now())


@app.route('/visitas')
@login_required
def visitas():
    estado = request.args.get('estado', 'todas')
    if estado == 'activas':
        lista_visitas = Visita.query.filter_by(fecha_salida=None).order_by(Visita.fecha_ingreso.desc()).all()
    elif estado == 'cerradas':
        lista_visitas = Visita.query.filter(Visita.fecha_salida!=None).order_by(Visita.fecha_ingreso.desc()).all()
    else:
        lista_visitas = Visita.query.order_by(Visita.fecha_ingreso.desc()).limit(100).all()
    return render_template('visitas.html', visitas=lista_visitas, estado=estado)


@app.route('/visitas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_visita():
    departamentos = Departamento.query.order_by(Departamento.numero).all()
    if request.method == 'POST':
        visita = Visita(
            nombre=request.form['nombre'],
            dni=request.form.get('dni'),
            departamento_id=request.form['departamento_id'],
            motivo=request.form['motivo'],
            usuario_registra_id=session['user_id']
        )
        db.session.add(visita)
        db.session.commit()
        flash('Visita registrada exitosamente', 'success')
        return redirect(url_for('visitas'))
    return render_template('nueva_visita.html', departamentos=departamentos)


@app.route('/visitas/salida/<int:id>')
@login_required
def salida_visita(id):
    visita = Visita.query.get_or_404(id)
    visita.fecha_salida = datetime.now()
    db.session.commit()
    flash('Salida registrada', 'success')
    return redirect(url_for('visitas'))


@app.route('/encomiendas')
@login_required
def encomiendas():
    estado = request.args.get('estado', 'todas')
    if estado == 'pendientes':
        lista_encomiendas = Encomienda.query.filter_by(fecha_retiro=None).order_by(Encomienda.fecha_recepcion.desc()).all()
    elif estado == 'retiradas':
        lista_encomiendas = Encomienda.query.filter(Encomienda.fecha_retiro!=None).order_by(Encomienda.fecha_recepcion.desc()).all()
    else:
        lista_encomiendas = Encomienda.query.order_by(Encomienda.fecha_recepcion.desc()).limit(100).all()
    return render_template('encomiendas.html', encomiendas=lista_encomiendas, estado=estado)


@app.route('/encomiendas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_encomienda():
    departamentos = Departamento.query.order_by(Departamento.numero).all()
    if request.method == 'POST':
        encomienda = Encomienda(
            departamento_id=request.form['departamento_id'],
            remitente=request.form.get('remitente'),
            descripcion=request.form['descripcion'],
            usuario_registra_id=session['user_id']
        )
        db.session.add(encomienda)
        db.session.commit()
        flash('Encomienda registrada', 'success')
        return redirect(url_for('encomiendas'))
    return render_template('nueva_encomienda.html', departamentos=departamentos)


@app.route('/encomiendas/retiro/<int:id>', methods=['GET', 'POST'])
@login_required
def retiro_encomienda(id):
    encomienda = Encomienda.query.get_or_404(id)
    if request.method == 'POST':
        encomienda.quien_retira = request.form['quien_retira']
        encomienda.fecha_retiro = datetime.now()
        db.session.commit()
        flash('Encomienda retirada', 'success')
        return redirect(url_for('encomiendas'))
    return render_template('retiro_encomienda.html', encomienda=encomienda)


@app.route('/estacionamiento')
@login_required
def estacionamiento():
    estado = request.args.get('estado', 'todas')
    if estado == 'ocupados':
        lista = Estacionamiento.query.filter_by(fecha_salida=None).order_by(Estacionamiento.fecha_ingreso.desc()).all()
    elif estado == 'libres':
        lista = Estacionamiento.query.filter(Estacionamiento.fecha_salida!=None).order_by(Estacionamiento.fecha_ingreso.desc()).all()
    else:
        lista = Estacionamiento.query.order_by(Estacionamiento.fecha_ingreso.desc()).limit(100).all()
    return render_template('estacionamiento.html', lista=lista, estado=estado)


@app.route('/estacionamiento/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_estacionamiento():
    departamentos = Departamento.query.order_by(Departamento.numero).all()
    
    plazas_vespucio = PlazaEstacionamiento.query.filter_by(sector='Vespucio').all()
    plazas_av = PlazaEstacionamiento.query.filter_by(sector='AV').all()
    
    plazas_vespucio_ocupadas = [e.plaza for e in Estacionamiento.query.filter_by(sector='Vespucio', fecha_salida=None).filter(Estacionamiento.plaza != None).all()]
    plazas_av_ocupadas = [e.plaza for e in Estacionamiento.query.filter_by(sector='AV', fecha_salida=None).filter(Estacionamiento.plaza != None).all()]
    
    if request.method == 'POST':
        auto = Estacionamiento(
            patente=request.form['patente'].upper(),
            departamento_id=request.form['departamento_id'],
            marca=request.form.get('marca'),
            color=request.form.get('color'),
            sector=request.form.get('sector'),
            plaza=request.form.get('plaza') if request.form.get('plaza') else None,
            usuario_registra_id=session['user_id']
        )
        db.session.add(auto)
        db.session.commit()
        flash('Estacionamiento registrado', 'success')
        return redirect(url_for('estacionamiento'))
    
    return render_template('nuevo_estacionamiento.html', 
                           departamentos=departamentos,
                           plazas_vespucio=plazas_vespucio,
                           plazas_av=plazas_av,
                           plazas_vespucio_ocupadas=plazas_vespucio_ocupadas,
                           plazas_av_ocupadas=plazas_av_ocupadas)


@app.route('/estacionamiento/salida/<int:id>')
@login_required
def salida_estacionamiento(id):
    auto = Estacionamiento.query.get_or_404(id)
    auto.fecha_salida = datetime.now()
    db.session.commit()
    flash('Salida de estacionamiento registrada', 'success')
    return redirect(url_for('estacionamiento'))


@app.route('/departamentos')
@login_required
@rol_required('admin', 'supervisor')
def departamentos():
    lista = Departamento.query.order_by(Departamento.numero).all()
    return render_template('departamentos.html', departamentos=lista)


@app.route('/departamentos/nuevo', methods=['GET', 'POST'])
@login_required
@rol_required('admin')
def nuevo_departamento():
    if request.method == 'POST':
        dept = Departamento(
            numero=request.form['numero'],
            piso=request.form['piso'],
            propietario=request.form['propietario']
        )
        db.session.add(dept)
        db.session.commit()
        flash('Departamento creado', 'success')
        return redirect(url_for('departamentos'))
    return render_template('nuevo_departamento.html')


@app.route('/usuarios')
@login_required
@rol_required('admin')
def usuarios():
    lista = User.query.all()
    return render_template('usuarios.html', usuarios=lista)


@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@rol_required('admin')
def nuevo_usuario():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            password=request.form['password'],
            nombre=request.form['nombre'],
            rol=request.form['rol']
        )
        db.session.add(user)
        db.session.commit()
        flash('Usuario creado', 'success')
        return redirect(url_for('usuarios'))
    return render_template('nuevo_usuario.html')


@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')


@app.route('/sw.js')
def service_worker():
    response = make_response(app.send_static_file('sw.js'))
    response.headers['Cache-Control'] = 'no-cache'
    return response


from flask import make_response

@app.route('/descargar')
def descargar_proyecto():
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        base_path = os.path.dirname(os.path.abspath(__file__))
        exclude = {'instance', '__pycache__', '.git', '.DS_Store'}
        for root, dirs, files in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in exclude]
            for file in files:
                if file not in exclude:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(base_path))
                    zf.write(file_path, arcname)
    memory_file.seek(0)
    return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name='condominio.zip')


def init_db():
    db.create_all()
    if not User.query.first():
        admin = User(username='admin', password='admin123', nombre='Administrador', rol='admin')
        supervisor = User(username='supervisor', password='super123', nombre='Supervisor', rol='supervisor')
        conserje = User(username='conserje', password='conserje123', nombre='Conserje', rol='conserje')
        db.session.add_all([admin, supervisor, conserje])
        
        deptos = []
        for piso in range(1, 9):
            for num in range(1, 19):
                deptos.append(Departamento(
                    numero=f'{piso}0{num}-1',
                    piso=piso,
                    propietario=f'Propietario Torre 1 P{piso}-{num:02d}'
                ))
        
        for piso in range(1, 9):
            for num in range(1, 19):
                deptos.append(Departamento(
                    numero=f'{piso}0{num}-2',
                    piso=piso,
                    propietario=f'Propietario Torre 2 P{piso}-{num:02d}'
                ))
        
        db.session.add_all(deptos)
        
        plazas = []
        for i in range(1, 7):
            plazas.append(PlazaEstacionamiento(numero=i, sector='Vespucio'))
        for i in range(1, 3):
            plazas.append(PlazaEstacionamiento(numero=i, sector='AV'))
        db.session.add_all(plazas)
        
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
