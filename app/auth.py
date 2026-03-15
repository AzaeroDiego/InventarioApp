from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Registrar nuevo usuario"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        nombre_completo = request.form.get('nombre_completo', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # Validaciones
        if not nombre_completo:
            flash('El nombre completo es requerido.', 'error')
            return redirect(url_for('auth.registro'))
        
        if not email or '@' not in email:
            flash('Email inválido.', 'error')
            return redirect(url_for('auth.registro'))
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
            return redirect(url_for('auth.registro'))
        
        if password != password_confirm:
            flash('Las contraseñas no coinciden.', 'error')
            return redirect(url_for('auth.registro'))
        
        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado.', 'error')
            return redirect(url_for('auth.registro'))
        
        # Crear nuevo usuario
        usuario = Usuario(nombre_completo=nombre_completo, email=email)
        usuario.set_password(password)
        
        db.session.add(usuario)
        db.session.commit()
        
        flash('Registro exitoso. Por favor inicia sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/registro.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Iniciar sesión"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_password(password) and usuario.activo:
            login_user(usuario, remember=request.form.get('recuerdame'))
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Email o contraseña inválidos.', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Sesión cerrada exitosamente.', 'success')
    return redirect(url_for('auth.login'))
