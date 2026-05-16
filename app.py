from flask import Flask, render_template_string, request, jsonify, session, redirect

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'grupo4_secret'

usuarios = {
    'demo@grupo4.com': {
        'nombre': 'Usuario Demo',
        'password': generate_password_hash('demo123'),
        'saldo': 5000000,
        'email': 'demo@grupo4.com'
    }
}

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GRUPO 4</title>

<style>
*{
margin:0;
padding:0;
box-sizing:border-box;
font-family:Arial,sans-serif;
}

body{
background:white;
}

header{
background:#d90000;
padding:20px 40px;
display:flex;
justify-content:space-between;
align-items:center;
color:white;
}

.logo{
font-size:60px;
font-weight:bold;
}

nav a{
color:white;
text-decoration:none;
margin-left:20px;
font-size:18px;
}

.hero{
background:linear-gradient(135deg,#d90000,#ff0000);
min-height:85vh;
display:flex;
justify-content:space-between;
align-items:center;
padding:60px;
color:white;
}

.left h1{
font-size:100px;
margin-bottom:20px;
}

.names{
font-size:32px;
line-height:1.5;
font-weight:bold;
margin-bottom:25px;
}

.left p{
font-size:38px;
line-height:1.4;
}

.login-box{
background:white;
padding:40px;
width:420px;
border-radius:20px;
color:black;
box-shadow:0 0 20px rgba(0,0,0,0.2);
}

.login-box h2{
text-align:center;
margin-bottom:25px;
font-size:36px;
color:#d90000;
}

.login-box input{
width:100%;
padding:15px;
margin-bottom:15px;
border-radius:10px;
border:1px solid #ccc;
font-size:18px;
}

.login-box button{
width:100%;
padding:15px;
border:none;
border-radius:10px;
background:#d90000;
color:white;
font-size:20px;
font-weight:bold;
cursor:pointer;
}

.section{
padding:80px 40px;
text-align:center;
}

.section h2{
font-size:48px;
margin-bottom:40px;
color:#d90000;
}

.cards{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
gap:25px;
}

.card{
background:white;
padding:30px;
border-radius:20px;
box-shadow:0 0 12px rgba(0,0,0,0.1);
}

.card h3{
font-size:28px;
margin-bottom:15px;
color:#d90000;
}

footer{
background:#d90000;
color:white;
padding:25px;
text-align:center;
font-size:20px;
}

@media(max-width:900px){
.hero{
flex-direction:column;
text-align:center;
}

.left h1{
font-size:70px;
}

.left p{
font-size:28px;
}

.login-box{
width:100%;
}
}
</style>
</head>

<body>

<header>
<div class="logo">GRUPO 4</div>

<nav>
<a href="/">Inicio</a>
<a href="/dashboard">Dashboard</a>
</nav>
</header>

<section class="hero">

<div class="left">
<h1>GRUPO 4</h1>

<div class="names">
Davesky Valery Camila Widelvis<br>
Rafael Anfitrion Jeury
</div>

<p>
Tu banco digital, donde estés.<br>
Fácil, rápido y seguro.
</p>
</div>

<div class="login-box">

<h2>Ingresa a tu cuenta</h2>

<form id="loginForm">
<input type="email" id="email" placeholder="Email">
<input type="password" id="password" placeholder="Contraseña">

<button type="submit">Ingresar</button>
</form>

<p style="margin-top:20px;text-align:center;">
demo@grupo4.com / demo123
</p>

</div>

</section>

<section class="section">

<h2>Descubre todo lo que puedes hacer</h2>

<div class="cards">

<div class="card">
<h3>🧮 Calculadora</h3>
<p>Calcula préstamos fácilmente.</p>
</div>

<div class="card">
<h3>📈 Inversiones</h3>
<p>Simula inversiones.</p>
</div>

<div class="card">
<h3>📰 Blog</h3>
<p>Noticias financieras.</p>
</div>

<div class="card">
<h3>👤 Dashboard</h3>
<p>Gestiona tu cuenta.</p>
</div>

</div>

</section>

<footer>
© 2026 GRUPO 4
</footer>

<script>
document.getElementById('loginForm').addEventListener('submit', async (e)=>{
e.preventDefault();

const email = document.getElementById('email').value;
const password = document.getElementById('password').value;

const response = await fetch('/login',{
method:'POST',
headers:{'Content-Type':'application/json'},
body:JSON.stringify({email,password})
});

const data = await response.json();

if(response.ok){
window.location.href='/dashboard';
}else{
alert(data.error);
}
});
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if email not in usuarios:
        return jsonify({'error':'Usuario incorrecto'}),401

    user = usuarios[email]

    if not check_password_hash(user['password'], password):
        return jsonify({'error':'Contraseña incorrecta'}),401

    session['email'] = email

    return jsonify({'ok':True})

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect('/')

    user = usuarios[session['email']]

    return f"""
    <h1>Bienvenido {user['nombre']}</h1>
    <h2>Saldo: ${user['saldo']}</h2>
    <a href='/'>Volver</a>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
