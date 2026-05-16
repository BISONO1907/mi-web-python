from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_super_segura_2026'

# Base de datos simulada (en producción usar SQLite/PostgreSQL)
usuarios = {
    'demo@scotiabank.cl': {
        'nombre': 'Usuario Demo',
        'password': generate_password_hash('demo123'),
        'saldo': 5000000,
        'email': 'demo@scotiabank.cl',
        'telefono': '+56912345678'
    }
}

articulos_blog = [
    {
        'id': 1,
        'titulo': 'Cómo ahorrar dinero en 2026',
        'autor': 'Grupo 4',
        'fecha': '2026-05-15',
        'contenido': 'Descubre las mejores estrategias para ahorrar dinero durante este año...',
        'imagen': '💰'
    },
    {
        'id': 2,
        'titulo': 'Inversiones seguras para principiantes',
        'autor': 'Asesor Financiero',
        'fecha': '2026-05-10',
        'contenido': 'Una guía completa para empezar en el mundo de las inversiones...',
        'imagen': '📈'
    },
    {
        'id': 3,
        'titulo': 'Impuestos 2026: Lo que debes saber',
        'autor': 'Departamento Legal',
        'fecha': '2026-05-05',
        'contenido': 'Información importante sobre las nuevas normativas fiscales...',
        'imagen': '📋'
    }
]

# ===================== RUTAS DE AUTENTICACIÓN =====================

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        datos = request.get_json()
        email = datos.get('email')
        nombre = datos.get('nombre')
        password = datos.get('password')
        telefono = datos.get('telefono', '')
        
        if email in usuarios:
            return jsonify({'error': 'El email ya está registrado'}), 400
        
        usuarios[email] = {
            'nombre': nombre,
            'password': generate_password_hash(password),
            'saldo': 0,
            'email': email,
            'telefono': telefono
        }
        
        return jsonify({'mensaje': 'Registro exitoso! Ahora puedes iniciar sesión'}), 201
    
    return render_template_string(TEMPLATE_REGISTRO)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        datos = request.get_json()
        email = datos.get('email')
        password = datos.get('password')
        
        if email not in usuarios:
            return jsonify({'error': 'Email o contraseña incorrectos'}), 401
        
        usuario = usuarios[email]
        if not check_password_hash(usuario['password'], password):
            return jsonify({'error': 'Email o contraseña incorrectos'}), 401
        
        session['email'] = email
        session['nombre'] = usuario['nombre']
        
        return jsonify({'mensaje': 'Login exitoso', 'redirect': '/dashboard'}), 200
    
    return render_template_string(TEMPLATE_LOGIN)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ===================== RUTAS PRINCIPALES =====================

@app.route('/')
def index():
    return render_template_string(TEMPLATE_INDEX)

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    usuario = usuarios[session['email']]
    return render_template_string(TEMPLATE_DASHBOARD, usuario=usuario)

# ===================== RUTAS DE FORMULARIOS Y CONTACTO =====================

@app.route('/api/contacto', methods=['POST'])
def contacto():
    datos = request.get_json()
    nombre = datos.get('nombre')
    email = datos.get('email')
    asunto = datos.get('asunto')
    mensaje = datos.get('mensaje')
    
    # Aquí iría la lógica de envío de email
    print(f"Nuevo contacto: {nombre} - {email} - {asunto}")
    
    return jsonify({'mensaje': 'Mensaje enviado exitosamente. Nos contactaremos pronto'}), 200

# ===================== RUTAS DE CALCULADORAS =====================

@app.route('/calculadora-prestamos')
def calculadora_prestamos():
    return render_template_string(TEMPLATE_CALCULADORA_PRESTAMOS)

@app.route('/api/calcular-prestamo', methods=['POST'])
def calcular_prestamo():
    datos = request.get_json()
    monto = float(datos.get('monto', 0))
    tasa_anual = float(datos.get('tasa', 4.5))
    meses = int(datos.get('meses', 12))
    
    # Fórmula: cuota = (monto * tasa_mensual) / (1 - (1 + tasa_mensual)^-meses)
    tasa_mensual = tasa_anual / 100 / 12
    cuota_mensual = (monto * tasa_mensual) / (1 - (1 + tasa_mensual) ** -meses)
    total_pagar = cuota_mensual * meses
    interes_total = total_pagar - monto
    
    return jsonify({
        'cuota_mensual': round(cuota_mensual, 2),
        'total_pagar': round(total_pagar, 2),
        'interes_total': round(interes_total, 2),
        'monto': monto,
        'meses': meses,
        'tasa': tasa_anual
    })

# ===================== RUTAS DE COTIZADOR DE SEGUROS =====================

@app.route('/cotizador-seguros')
def cotizador_seguros():
    return render_template_string(TEMPLATE_COTIZADOR_SEGUROS)

@app.route('/api/cotizar-seguro', methods=['POST'])
def cotizar_seguro():
    datos = request.get_json()
    tipo = datos.get('tipo')
    valor_bien = float(datos.get('valor_bien', 0))
    
    tasas = {
        'vida': 0.8,           # 0.8% anual
        'auto': 2.5,           # 2.5% anual
        'hogar': 1.2,          # 1.2% anual
        'salud': 1.5           # 1.5% anual
    }
    
    tasa = tasas.get(tipo, 1.0)
    prima_anual = (valor_bien * tasa) / 100
    prima_mensual = prima_anual / 12
    
    beneficios = {
        'vida': ['Cobertura hasta $500M', 'Beneficiarios protegidos', 'Asistencia 24/7'],
        'auto': ['Cobertura total', 'Asistencia en ruta', 'Taller de confianza'],
        'hogar': ['Cobertura de incendios', 'Robo y asalto', 'Responsabilidad civil'],
        'salud': ['Cobertura ambulatoria', 'Hospitalización', 'Medicamentos']
    }
    
    return jsonify({
        'tipo': tipo,
        'valor_bien': valor_bien,
        'prima_mensual': round(prima_mensual, 2),
        'prima_anual': round(prima_anual, 2),
        'tasa': tasa,
        'beneficios': beneficios.get(tipo, [])
    })

# ===================== RUTAS DEL BLOG =====================

@app.route('/blog')
def blog():
    return render_template_string(TEMPLATE_BLOG, articulos=articulos_blog)

@app.route('/blog/<int:id>')
def articulo_detalle(id):
    articulo = next((a for a in articulos_blog if a['id'] == id), None)
    if not articulo:
        return redirect(url_for('blog'))
    return render_template_string(TEMPLATE_ARTICULO, articulo=articulo)

@app.route('/api/blog')
def api_blog():
    return jsonify(articulos_blog)

# ===================== RUTAS DEL SIMULADOR DE INVERSIONES =====================

@app.route('/simulador-inversiones')
def simulador_inversiones():
    return render_template_string(TEMPLATE_SIMULADOR_INVERSIONES)

@app.route('/api/simular-inversion', methods=['POST'])
def simular_inversion():
    datos = request.get_json()
    capital_inicial = float(datos.get('capital', 0))
    rendimiento_anual = float(datos.get('rendimiento', 5.0))
    anos = int(datos.get('anos', 5))
    
    # Fórmula de interés compuesto: A = P(1 + r)^t
    tasa_decimal = rendimiento_anual / 100
    resultados = []
    
    for ano in range(anos + 1):
        monto = capital_inicial * ((1 + tasa_decimal) ** ano)
        ganancia = monto - capital_inicial
        resultados.append({
            'ano': ano,
            'monto': round(monto, 2),
            'ganancia': round(ganancia, 2)
        })
    
    monto_final = capital_inicial * ((1 + tasa_decimal) ** anos)
    ganancia_total = monto_final - capital_inicial
    
    return jsonify({
        'capital_inicial': capital_inicial,
        'rendimiento_anual': rendimiento_anual,
        'anos': anos,
        'monto_final': round(monto_final, 2),
        'ganancia_total': round(ganancia_total, 2),
        'resultados': resultados
    })

# ===================== TEMPLATES HTML =====================

TEMPLATE_INDEX = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grupo 4</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; }
        
        header {
            background: linear-gradient(135deg, #d90000 0%, #a00000 100%);
            color: white;
            padding: 16px 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo { font-size: 24px; font-weight: bold; }
        
        nav { display: flex; gap: 20px; align-items: center; }
        nav a { color: white; text-decoration: none; font-size: 14px; transition: opacity 0.3s; }
        nav a:hover { opacity: 0.8; }
        
        .nav-cta { background: #ff6b35; padding: 8px 16px; border-radius: 4px; color: white !important; }
        .nav-cta:hover { background: #e55a24; }
        
        .hero {
            background: linear-gradient(135deg, #d90000 0%, #0066cc 100%);
            color: white;
            padding: 80px 20px;
            text-align: center;
        }
        
        .hero h1 { font-size: 48px; margin-bottom: 20px; }
        .hero p { font-size: 18px; margin-bottom: 30px; opacity: 0.95; }
        
        .hero-buttons { display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; }
        
        .btn {
            padding: 12px 32px;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-primary { background: #ff6b35; color: white; }
        .btn-primary:hover { background: #e55a24; transform: translateY(-2px); }
        
        .btn-secondary { background: white; color: #d90000; border: 2px solid white; }
        .btn-secondary:hover { background: transparent; color: white; }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        
        .features {
            padding: 80px 20px;
            background: white;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 24px;
        }
        
        .feature-card {
            background: #f8f9fa;
            padding: 32px 24px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #ff6b35;
            transition: transform 0.3s;
        }
        
        .feature-card:hover { transform: translateY(-4px); }
        .feature-card h3 { color: #d90000; margin-bottom: 12px; }
        .feature-card .icon { font-size: 40px; margin-bottom: 16px; }
        
        footer {
            background: #1a1a1a;
            color: #999;
            padding: 40px 20px;
            text-align: center;
            font-size: 12px;
        }
        
        @media (max-width: 768px) {
            .hero h1 { font-size: 32px; }
            nav { gap: 10px; font-size: 12px; }
            .hero-buttons { flex-direction: column; }
            .btn { width: 100%; }
        }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="logo">GRUPO 4</div>
            <nav>
                <a href="/">Inicio</a>
                <a href="/blog">Blog</a>
                <a href="/calculadora-prestamos">Calculadora</a>
                <a href="/cotizador-seguros">Seguros</a>
                <a href="/simulador-inversiones">Inversiones</a>
                <a class="nav-cta" href="/login">Iniciar Sesión</a>
            </nav>
        </div>
    </header>

    <section class="hero">
        <div class="container">
            <h1>GRUPO 4</h1>
            <p style="font-size:28px; font-weight:bold; line-height:1.6;">
Davesky Valery Camila Widelvis<br>
Rafael Anfitrion Jeury
</p>

<p>Accede a tus cuentas, realiza transferencias y gestiona tus inversiones desde cualquier lugar</p>
            <div class="hero-buttons">
                <button class="btn btn-primary" onclick="window.location.href='/registro'">Registrarse</button>
                <button class="btn btn-secondary" onclick="window.location.href='/dashboard'">Acceder</button>
            </div>
        </div>
    </section>

    <section class="features">
        <div class="container">
            <h2 style="text-align: center; color: #d90000; margin-bottom: 50px; font-size: 36px;">Nuestras Herramientas</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="icon">🧮</div>
                    <h3>Calculadora de Préstamos</h3>
                    <p>Simula cuotas mensuales y totales de forma inmediata</p>
                    <a href="/calculadora-prestamos" class="btn btn-primary" style="margin-top: 16px;">Usar</a>
                </div>
                <div class="feature-card">
                    <div class="icon">🛡️</div>
                    <h3>Cotizador de Seguros</h3>
                    <p>Obtén cotizaciones de seguros en segundos</p>
                    <a href="/cotizador-seguros" class="btn btn-primary" style="margin-top: 16px;">Usar</a>
                </div>
                <div class="feature-card">
                    <div class="icon">📊</div>
                    <h3>Simulador de Inversiones</h3>
                    <p>Proyecta tus ganancias con interés compuesto</p>
                    <a href="/simulador-inversiones" class="btn btn-primary" style="margin-top: 16px;">Usar</a>
                </div>
                <div class="feature-card">
                    <div class="icon">📰</div>
                    <h3>Blog de Finanzas</h3>
                    <p>Artículos y tips de educación financiera</p>
                    <a href="/blog" class="btn btn-primary" style="margin-top: 16px;">Leer</a>
                </div>
                <div class="feature-card">
                    <div class="icon">👤</div>
                    <h3>Tu Dashboard</h3>
                    <p>Gestiona tu perfil y fondos personales</p>
                    <a href="/dashboard" class="btn btn-primary" style="margin-top: 16px;">Ingresar</a>
                </div>
                <div class="feature-card">
                    <div class="icon">📞</div>
                    <h3>Contáctanos</h3>
                    <p>Estamos disponibles 24/7 para ayudarte</p>
                    <a href="#" class="btn btn-primary" style="margin-top: 16px;">Escribir</a>
                </div>
            </div>
        </div>
    </section>

    <footer>
        <p>&copy; 2026 Grupo 4 Chile. Todos los derechos reservados.</p>
    </footer>
</body>
</html>
'''

TEMPLATE_LOGIN = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iniciar Sesión - Grupo 4</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; }
        
        header {
            background: linear-gradient(135deg, #d90000 0%, #a00000 100%);
            color: white;
            padding: 16px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .header-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .logo { font-size: 24px; font-weight: bold; }
        
        .container {
            max-width: 400px;
            margin: 60px auto;
            padding: 0 20px;
        }
        
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        }
        
        .login-box h1 { color: #d90000; margin-bottom: 30px; text-align: center; font-size: 28px; }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        
        input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            transition: border 0.3s;
        }
        
        input:focus {
            outline: none;
            border-color: #d90000;
            box-shadow: 0 0 0 3px rgba(0,74,151,0.1);
        }
        
        .btn {
            width: 100%;
            padding: 12px;
            background: #ff6b35;
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .btn:hover { background: #e55a24; }
        
        .signup-link {
            text-align: center;
            margin-top: 20px;
            color: #666;
        }
        
        .signup-link a {
            color: #d90000;
            text-decoration: none;
            font-weight: 600;
        }
        
        .alert { padding: 12px; margin-bottom: 20px; border-radius: 4px; display: none; }
        .alert.error { background: #ffe6e6; color: #d32f2f; border: 1px solid #d32f2f; }
        .alert.success { background: #e8f5e9; color: #388e3c; border: 1px solid #388e3c; }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="logo">GRUPO 4</div>
        </div>
    </header>

    <div class="container">
        <div class="login-box">
            <h1>Iniciar Sesión</h1>
            <div class="alert" id="alert"></div>
            
            <form id="loginForm">
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Contraseña</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <button type="submit" class="btn">Iniciar Sesión</button>
            </form>
            
            <div class="signup-link">
                ¿No tienes cuenta? <a href="/registro">Regístrate aquí</a>
            </div>
            
            <div style="margin-top: 20px; padding: 12px; background: #f0f4f9; border-radius: 4px; font-size: 12px;">
                <strong>Demo:</strong><br>
                Email: demo@scotiabank.cl<br>
                Contraseña: demo123
            </div>
        </div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const alert = document.getElementById('alert');
            
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    alert.className = 'alert success';
                    alert.textContent = data.mensaje;
                    alert.style.display = 'block';
                    setTimeout(() => window.location.href = data.redirect, 1500);
                } else {
                    alert.className = 'alert error';
                    alert.textContent = data.error;
                    alert.style.display = 'block';
                }
            } catch (error) {
                alert.className = 'alert error';
                alert.textContent = 'Error de conexión';
                alert.style.display = 'block';
            }
        });
    </script>
</body>
</html>
'''

TEMPLATE_REGISTRO = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registro - Grupo 4</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; }
        
        header {
            background: linear-gradient(135deg, #d90000 0%, #a00000 100%);
            color: white;
            padding: 16px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .header-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .logo { font-size: 24px; font-weight: bold; }
        
        .container {
            max-width: 400px;
            margin: 40px auto;
            padding: 0 20px;
        }
        
        .registro-box {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        }
        
        .registro-box h1 { color: #d90000; margin-bottom: 30px; text-align: center; font-size: 28px; }
        
        .form-group { margin-bottom: 20px; }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        
        input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        input:focus {
            outline: none;
            border-color: #d90000;
        }
        
        .btn {
            width: 100%;
            padding: 12px;
            background: #ff6b35;
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: 600;
            cursor: pointer;
        }
        
        .btn:hover { background: #e55a24; }
        
        .login-link {
            text-align: center;
            margin-top: 20px;
        }
        
        .login-link a {
            color: #d90000;
            text-decoration: none;
            font-weight: 600;
        }
        
        .alert { padding: 12px; margin-bottom: 20px; border-radius: 4px; display: none; }
        .alert.error { background: #ffe6e6; color: #d32f2f; }
        .alert.success { background: #e8f5e9; color: #388e3c; }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="logo">GRUPO 4</div>
        </div>
    </header>

    <div class="container">
        <div class="registro-box">
            <h1>Crear Cuenta</h1>
            <div class="alert" id="alert"></div>
            
            <form id="registroForm">
                <div class="form-group">
                    <label for="nombre">Nombre Completo</label>
                    <input type="text" id="nombre" name="nombre" required>
                </div>
                
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="telefono">Teléfono</label>
                    <input type="tel" id="telefono" name="telefono">
                </div>
                
                <div class="form-group">
                    <label for="password">Contraseña</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <button type="submit" class="btn">Registrarse</button>
            </form>
            
            <div class="login-link">
                ¿Ya tienes cuenta? <a href="/login">Inicia sesión</a>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('registroForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const nombre = document.getElementById('nombre').value;
            const email = document.getElementById('email').value;
            const telefono = document.getElementById('telefono').value;
            const password = document.getElementById('password').value;
            const alert = document.getElementById('alert');
            
            try {
                const response = await fetch('/registro', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nombre, email, telefono, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    alert.className = 'alert success';
                    alert.textContent = data.mensaje;
                    alert.style.display = 'block';
                    setTimeout(() => window.location.href = '/login', 2000);
                } else {
                    alert.className = 'alert error';
                    alert.textContent = data.error;
                    alert.style.display = 'block';
                }
            } catch (error) {
                alert.className = 'alert error';
                alert.textContent = 'Error de conexión';
                alert.style.display = 'block';
            }
        });
    </script>
</body>
</html>
'''

TEMPLATE_DASHBOARD = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Grupo 4</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; }
        
        header {
            background: linear-gradient(135deg, #d90000 0%, #a00000 100%);
            color: white;
            padding: 16px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo { font-size: 24px; font-weight: bold; }
        
        nav { display: flex; gap: 20px; align-items: center; }
        nav a { color: white; text-decoration: none; }
        
        .logout-btn {
            background: #ff6b35;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        .welcome { padding: 20px; background: white; margin-bottom: 20px; border-radius: 8px; }
        .welcome h1 { color: #d90000; margin-bottom: 10px; }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            padding: 24px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .card h3 { color: #d90000; margin-bottom: 12px; }
        .card .amount { font-size: 32px; font-weight: bold; color: #ff6b35; }
        .card p { color: #666; font-size: 14px; }
        
        .tools-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }
        
        .tool-btn {
            padding: 16px;
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            color: #d90000;
            font-weight: 600;
        }
        
        .tool-btn:hover {
            background: #d90000;
            color: white;
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="logo">GRUPO 4</div>
            <nav>
                <a href="/">Inicio</a>
                <a href="/blog">Blog</a>
                <a class="logout-btn" href="/logout">Cerrar Sesión</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <div class="welcome">
            <h1>Bienvenido, {{ usuario.nombre }}!</h1>
            <p>Email: {{ usuario.email }} | Teléfono: {{ usuario.telefono }}</p>
        </div>

        <div class="dashboard-grid">
            <div class="card">
                <h3>Saldo Total</h3>
                <div class="amount">${{ "%.2f"|format(usuario.saldo) }}</div>
                <p>En tu cuenta corriente</p>
            </div>
            <div class="card">
                <h3>Transacciones</h3>
                <div class="amount">0</div>
                <p>Este mes</p>
            </div>
            <div class="card">
                <h3>Inversiones</h3>
                <div class="amount">$0</div>
                <p>Valor actual</p>
            </div>
        </div>

        <h2 style="color: #d90000; margin-bottom: 20px;">Herramientas Disponibles</h2>
        <div class="tools-grid">
            <a href="/calculadora-prestamos" class="tool-btn">🧮 Calculadora de Préstamos</a>
            <a href="/cotizador-seguros" class="tool-btn">🛡️ Cotizador de Seguros</a>
            <a href="/simulador-inversiones" class="tool-btn">📊 Simulador de Inversiones</a>
            <a href="/blog" class="tool-btn">📰 Blog Financiero</a>
        </div>
    </div>
</body>
</html>
'''

TEMPLATE_CALCULADORA_PRESTAMOS = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculadora de Préstamos - Grupo 4</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; }
        
        header {
            background: linear-gradient(135deg, #d90000 0%, #a00000 100%);
            color: white;
            padding: 16px 0;
        }
        
        .header-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; }
        nav { display: flex; gap: 20px; }
        nav a { color: white; text-decoration: none; }
        
        .container { max-width: 800px; margin: 40px auto; padding: 0 20px; }
        
        .calculator {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        }
        
        h1 { color: #d90000; margin-bottom: 30px; text-align: center; }
        
        .form-group {
            margin-bottom: 24px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        
        input, select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .range-display {
            display: flex;
            justify-content: space-between;
            margin-top: 8px;
            color: #666;
            font-size: 12px;
        }
        
        button {
            width: 100%;
            padding: 12px;
            background: #ff6b35;
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: 600;
            cursor: pointer;
            font-size: 16px;
        }
        
        button:hover { background: #e55a24; }
        
        .results {
            margin-top: 40px;
            padding: 24px;
            background: #f0f4f9;
            border-radius: 8px;
            display: none;
        }
        
        .results.show { display: block; }
        
        .result-item {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #ddd;
        }
        
        .result-item:last-child { border-bottom: none; }
        .result-item strong { color: #d90000; }
        .result-item .value { font-weight: bold; color: #ff6b35; }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="logo">GRUPO 4</div>
            <nav>
                <a href="/">Inicio</a>
                <a href="/dashboard">Dashboard</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <div class="calculator">
            <h1>🧮 Calculadora de Préstamos</h1>
            
            <form id="prestamoForm">
                <div class="form-group">
                    <label for="monto">Monto del Préstamo ($)</label>
                    <input type="number" id="monto" name="monto" min="0" max="100000000" value="5000000" step="100000" required>
                </div>
                
                <div class="form-group">
                    <label for="tasa">Tasa de Interés Anual (%)</label>
                    <input type="number" id="tasa" name="tasa" min="0" max="30" value="4.5" step="0.1" required>
                </div>
                
                <div class="form-group">
                    <label for="meses">Plazo (meses)</label>
                    <input type="range" id="meses" name="meses" min="6" max="360" value="60" step="1">
                    <div class="range-display">
                        <span>6 meses</span>
                        <span id="mesesVal">60 meses</span>
                        <span>30 años</span>
                    </div>
                </div>
                
                <button type="submit">Calcular</button>
            </form>
            
            <div class="results" id="results">
                <div class="result-item">
                    <strong>Cuota Mensual:</strong>
                    <span class="value" id="cuotaMensual">$0</span>
                </div>
                <div class="result-item">
                    <strong>Total a Pagar:</strong>
                    <span class="value" id="totalPagar">$0</span>
                </div>
                <div class="result-item">
                    <strong>Intereses Totales:</strong>
                    <span class="value" id="interesToltal">$0</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('meses').addEventListener('change', (e) => {
            document.getElementById('mesesVal').textContent = e.target.value + ' meses';
        });
        
        document.getElementById('prestamoForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const monto = document.getElementById('monto').value;
            const tasa = document.getElementById('tasa').value;
            const meses = document.getElementById('meses').value;
            
            try {
                const response = await fetch('/api/calcular-prestamo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ monto, tasa, meses })
                });
                
                const data = await response.json();
                
                document.getElementById('cuotaMensual').textContent = 
                    '$' + data.cuota_mensual.toLocaleString('es-CL');
                document.getElementById('totalPagar').textContent = 
                    '$' + data.total_pagar.toLocaleString('es-CL');
                document.getElementById('interesToltal').textContent = 
                    '$' + data.interes_total.toLocaleString('es-CL');
                
                document.getElementById('results').classList.add('show');
            } catch (error) {
                alert('Error al calcular');
            }
        });
    </script>
</body>
</html>
'''

TEMPLATE_COTIZADOR_SEGUROS = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cotizador de Seguros - Grupo 4</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; }
        
        header {
            background: linear-gradient(135deg, #d90000 0%, #a00000 100%);
            color: white;
            padding: 16px 0;
        }
        
        .header-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; }
        nav { display: flex; gap: 20px; }
        nav a { color: white; text-decoration: none; }
        
        .container { max-width: 800px; margin: 40px auto; padding: 0 20px; }
        
        .cotizador {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        }
        
        h1 { color: #d90000; margin-bottom: 30px; text-align: center; }
        
        .form-group { margin-bottom: 24px; }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        
        select, input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        button {
            width: 100%;
            padding: 12px;
            background: #ff6b35;
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: 600;
            cursor: pointer;
        }
        
        button:hover { background: #e55a24; }
        
        .results {
            margin-top: 40px;
            display: none;
        }
        
        .results.show { display: block; }
        
        .quote-card {
            background: #f0f4f9;
            padding: 24px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .quote-card h3 { color: #d90000; margin-bottom: 16px; }
        
        .price-section {
            background: white;
            padding: 16px;
            border-radius: 4px;
            margin-bottom: 16px;
        }
        
        .price-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        
        .price-item strong { color: #d90000; }
        .price-item .value { font-weight: bold; color: #ff6b35; font-size: 18px; }
        
        .benefits {
            background: white;
            padding: 16px;
            border-radius: 4px;
        }
        
        .benefits h4 { color: #d90000; margin-bottom: 12px; font-size: 14px; }
        
        .benefit-item {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            font-size: 13px;
        }
        
        .benefit-item:before {
            content: "✓";
            color: #ff6b35;
            font-weight: bold;
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="logo">GRUPO 4</div>
            <nav>
                <a href="/">Inicio</a>
                <a href="/dashboard">Dashboard</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <div class="cotizador">
            <h1>🛡️ Cotizador de Seguros</h1>
            
            <form id="seguroForm">
                <div class="form-group">
                    <label for="tipo">Tipo de Seguro</label>
                    <select id="tipo" name="tipo" required>
                        <option value="">Selecciona un tipo</option>
                        <option value="vida">Seguro de Vida</option>
                        <option value="auto">Seguro de Auto</option>
                        <option value="hogar">Seguro de Hogar</option>
                        <option value="salud">Seguro de Salud</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="valor">Valor del Bien ($)</label>
                    <input type="number" id="valor" name="valor" min="0" max="1000000000" value="50000000" step="1000000" required>
                </div>
                
                <button type="submit">Cotizar</button>
            </form>
            
            <div class="results" id="results">
                <div class="quote-card">
                    <h3 id="seguroTitulo"></h3>
                    
                    <div class="price-section">
                        <div class="price-item">
                            <strong>Prima Mensual:</strong>
                            <span class="value" id="primaMensual">$0</span>
                        </div>
                        <div class="price-item">
                            <strong>Prima Anual:</strong>
                            <span class="value" id="primaAnual">$0</span>
                        </div>
                    </div>
                    
                    <div class="benefits">
                        <h4>Beneficios Incluidos:</h4>
                        <div id="beneficios"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('seguroForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const tipo = document.getElementById('tipo').value;
            const valor_bien = document.getElementById('valor').value;
            
            try {
                const response = await fetch('/api/cotizar-seguro', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tipo, valor_bien })
                });
                
                const data = await response.json();
                
                const tiposNombres = {
                    'vida': 'Seguro de Vida',
                    'auto': 'Seguro de Auto',
                    'hogar': 'Seguro de Hogar',
                    'salud': 'Seguro de Salud'
                };
                
                document.getElementById('seguroTitulo').textContent = tiposNombres[tipo];
                document.getElementById('primaMensual').textContent = 
                    '$' + data.prima_mensual.toLocaleString('es-CL');
                document.getElementById('primaAnual').textContent = 
                    '$' + data.prima_anual.toLocaleString('es-CL');
                
                const beneficiosHtml = data.beneficios.map(b => 
                    `<div class="benefit-item">${b}</div>`
                ).join('');
                
                document.getElementById('beneficios').innerHTML = beneficiosHtml;
                document.getElementById('results').classList.add('show');
            } catch (error) {
                alert('Error al cotizar');
            }
        });
    </script>
</body>
</html>
'''

TEMPLATE_BLOG = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog - Grupo 4</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; }
        
        header {
            background: linear-gradient(135deg, #d90000 0%, #a00000 100%);
            color: white;
            padding: 16px 0;
        }
        
        .header-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; }
        nav { display: flex; gap: 20px; }
        nav a { color: white; text-decoration: none; }
        
        .container { max-width: 1000px; margin: 40px auto; padding: 0 20px; }
        
        h1 { color: #d90000; text-align: center; margin-bottom: 40px; }
        
        .blog-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
        }
        
        .blog-card {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s;
            cursor: pointer;
        }
        
        .blog-card:hover { transform: translateY(-4px); }
        
        .blog-image {
            background: #f0f4f9;
            padding: 30px;
            text-align: center;
            font-size: 48px;
            border-bottom: 1px solid #ddd;
        }
        
        .blog-content {
            padding: 20px;
        }
        
        .blog-date {
            color: #999;
            font-size: 12px;
            margin-bottom: 8px;
        }
        
        .blog-title {
            color: #d90000;
            margin-bottom: 12px;
            font-size: 18px;
        }
        
        .blog-excerpt {
            color: #666;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 16px;
        }
        
        .blog-author {
            color: #999;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="logo">GRUPO 4</div>
            <nav>
                <a href="/">Inicio</a>
                <a href="/dashboard">Dashboard</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <h1>📰 Blog Financiero</h1>
        
        <div class="blog-grid">
            {% for articulo in articulos %}
            <div class="blog-card" onclick="window.location.href='/blog/{{ articulo.id }}'">
                <div class="blog-image">{{ articulo.imagen }}</div>
                <div class="blog-content">
                    <div class="blog-date">{{ articulo.fecha }}</div>
                    <div class="blog-title">{{ articulo.titulo }}</div>
                    <div class="blog-excerpt">{{ articulo.contenido }}</div>
                    <div class="blog-author">Por: {{ articulo.autor }}</div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

TEMPLATE_ARTICULO = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ articulo.titulo }} - Grupo 4</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; }
        
        header {
            background: linear-gradient(135deg, #d90000 0%, #a00000 100%);
            color: white;
            padding: 16px 0;
        }
        
        .header-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; }
        nav { display: flex; gap: 20px; }
        nav a { color: white; text-decoration: none; }
        
        .container { max-width: 700px; margin: 40px auto; padding: 0 20px; }
        
        .article {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .article-image {
            text-align: center;
            font-size: 80px;
            margin-bottom: 30px;
        }
        
        .article-title {
            color: #d90000;
            font-size: 32px;
            margin-bottom: 16px;
        }
        
        .article-meta {
            color: #999;
            font-size: 14px;
            margin-bottom: 30px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 16px;
        }
        
        .article-content {
            color: #333;
            line-height: 1.8;
            font-size: 16px;
        }
        
        .back-link {
            margin-top: 30px;
            display: inline-block;
            color: #d90000;
            text-decoration: none;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="logo">GRUPO 4</div>
            <nav>
                <a href="/">Inicio</a>
                <a href="/blog">Blog</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <div class="article">
            <div class="article-image">{{ articulo.imagen }}</div>
            <h1 class="article-title">{{ articulo.titulo }}</h1>
            <div class="article-meta">
                Publicado: {{ articulo.fecha }} | Por: {{ articulo.autor }}
            </div>
            <div class="article-content">
                <p>{{ articulo.contenido }}</p>
                <p style="margin-top: 20px;">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
            </div>
            <a href="/blog" class="back-link">← Volver al blog</a>
        </div>
    </div>
</body>
</html>
'''

TEMPLATE_SIMULADOR_INVERSIONES = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulador de Inversiones - Grupo 4</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; }
        
        header {
            background: linear-gradient(135deg, #d90000 0%, #a00000 100%);
            color: white;
            padding: 16px 0;
        }
        
        .header-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; }
        nav { display: flex; gap: 20px; }
        nav a { color: white; text-decoration: none; }
        
        .container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
        
        .simulator {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        }
        
        h1 { color: #d90000; margin-bottom: 30px; text-align: center; }
        
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .form-group { margin-bottom: 0; }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
            font-size: 14px;
        }
        
        input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        button {
            grid-column: 1 / -1;
            padding: 12px;
            background: #ff6b35;
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: 600;
            cursor: pointer;
        }
        
        button:hover { background: #e55a24; }
        
        .results {
            margin-top: 40px;
            display: none;
        }
        
        .results.show { display: block; }
        
        .summary {
            background: #f0f4f9;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .summary-item {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #ddd;
        }
        
        .summary-item:last-child { border-bottom: none; }
        .summary-item strong { color: #d90000; }
        .summary-item .value { font-weight: bold; color: #ff6b35; }
        
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #ddd;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        
        th, td {
            padding: 12px;
            text-align: right;
            border-bottom: 1px solid #ddd;
        }
        
        th {
            background: #f0f4f9;
            color: #d90000;
            font-weight: 600;
        }
        
        th:first-child, td:first-child { text-align: left; }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="logo">GRUPO 4</div>
            <nav>
                <a href="/">Inicio</a>
                <a href="/dashboard">Dashboard</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <div class="simulator">
            <h1>📊 Simulador de Inversiones</h1>
            
            <form id="inversionForm" class="form-grid">
                <div class="form-group">
                    <label for="capital">Capital Inicial ($)</label>
                    <input type="number" id="capital" name="capital" min="0" max="1000000000" value="10000000" step="100000" required>
                </div>
                
                <div class="form-group">
                    <label for="rendimiento">Rendimiento Anual (%)</label>
                    <input type="number" id="rendimiento" name="rendimiento" min="0" max="50" value="8" step="0.5" required>
                </div>
                
                <div class="form-group">
                    <label for="anos">Años a Invertir</label>
                    <input type="number" id="anos" name="anos" min="1" max="50" value="10" step="1" required>
                </div>
                
                <button type="submit">Simular</button>
            </form>
            
            <div class="results" id="results">
                <div class="summary">
                    <div class="summary-item">
                        <strong>Capital Inicial:</strong>
                        <span class="value" id="capitalInicial">$0</span>
                    </div>
                    <div class="summary-item">
                        <strong>Monto Final:</strong>
                        <span class="value" id="montoFinal">$0</span>
                    </div>
                    <div class="summary-item">
                        <strong>Ganancia Total:</strong>
                        <span class="value" id="gananciaToltal">$0</span>
                    </div>
                </div>
                
                <div class="chart-container">
                    <h3 style="color: #d90000; margin-bottom: 16px;">Proyección Año a Año</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Año</th>
                                <th>Valor Total</th>
                                <th>Ganancia</th>
                            </tr>
                        </thead>
                        <tbody id="tableBody"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('inversionForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const capital = document.getElementById('capital').value;
            const rendimiento = document.getElementById('rendimiento').value;
            const anos = document.getElementById('anos').value;
            
            try {
                const response = await fetch('/api/simular-inversion', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ capital, rendimiento, anos })
                });
                
                const data = await response.json();
                
                document.getElementById('capitalInicial').textContent = 
                    '$' + data.capital_inicial.toLocaleString('es-CL');
                document.getElementById('montoFinal').textContent = 
                    '$' + data.monto_final.toLocaleString('es-CL');
                document.getElementById('gananciaToltal').textContent = 
                    '$' + data.ganancia_total.toLocaleString('es-CL');
                
                const tableBody = document.getElementById('tableBody');
                tableBody.innerHTML = data.resultados.map(r => `
                    <tr>
                        <td>${r.ano}</td>
                        <td>$${r.monto.toLocaleString('es-CL')}</td>
                        <td>$${r.ganancia.toLocaleString('es-CL')}</td>
                    </tr>
                `).join('');
                
                document.getElementById('results').classList.add('show');
            } catch (error) {
                alert('Error al simular');
            }
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True, port=5000)
