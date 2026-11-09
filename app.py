from flask import Flask, render_template, request, redirect, url_for, session, abort
import sqlite3
import os
import secrets

app = Flask(__name__)
app.secret_key = 'clave_super_secreta_tpi_2026'
DATABASE = 'afinar.db'

# ---------------------------------------------------------------
# CONFIGURACIÓN DE SEGURIDAD DE SESIÓN (Protección contra robo de cookies)
# ---------------------------------------------------------------
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,   # Impide acceso a la cookie de sesión desde JavaScript (Anti-XSS)
    SESSION_COOKIE_SAMESITE='Lax',  # Mitigación base contra CSRF en cookies
)


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------
# PROTECCIÓN CSRF (Cross-Site Request Forgery)
# ---------------------------------------------------------------
@app.before_request
def csrf_protect():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)

    if request.method == 'POST':
        token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
        if not token or token != session.get('csrf_token'):
            abort(403)


@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=session.get('csrf_token', ''))


# ---------------------------------------------------------------
# CABECERAS DE SEGURIDAD (Anti-Clickjacking, Anti-MIME sniffing, CSP Anti-XSS)
# ---------------------------------------------------------------
@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "font-src 'self' https://fonts.gstatic.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "img-src 'self' data: https://images.unsplash.com; "
        "script-src 'self' 'unsafe-inline'; "
        "frame-ancestors 'self';"
    )
    return response


# ---------------------------------------------------------------
# INICIO
# ---------------------------------------------------------------
@app.route('/')
def index():
    return redirect(url_for('catalogo'))


# ---------------------------------------------------------------
# LOGIN  ✅ SEGURO: CONSULTAS PARAMETRIZADAS + PROTECCIÓN CSRF
# ---------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        conn = get_db()
        try:
            # ✅ SEGURO: Parámetros posicionales '?'
            query = "SELECT * FROM usuarios WHERE username = ? AND password = ?"
            user = conn.execute(query, (username, password)).fetchone()
            conn.close()

            if user:
                # Anti-Session Fixation: se regenera la sesión en el inicio exitoso
                session.clear()
                session['csrf_token'] = secrets.token_hex(32)
                session['user'] = dict(user)
                return redirect(url_for('catalogo'))
            else:
                error = 'Usuario o contraseña incorrectos.'
        except Exception:
            conn.close()
            error = 'Error en la autenticación. Por favor, intente nuevamente.'

    return render_template('login.html', error=error)


# ---------------------------------------------------------------
# MI CUENTA / PERFIL  ✅ PROTEGIDO CONTRA IDOR
#   No recibe un 'user_id' por URL. Consulta estrictamente el ID
#   almacenado en la sesión autenticada en el servidor.
# ---------------------------------------------------------------
@app.route('/perfil')
def perfil():
    if not session.get('user'):
        return redirect(url_for('login'))

    user_id = session['user']['id']
    conn = get_db()
    user = conn.execute('SELECT id, username, email, rol FROM usuarios WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if not user:
        return redirect(url_for('logout'))

    return render_template('perfil.html', user=user)


# ---------------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------------------------------------------------------------
# CATÁLOGO (Público)
# ---------------------------------------------------------------
@app.route('/catalogo')
def catalogo():
    categoria = request.args.get('categoria', '').strip()
    conn = get_db()
    if categoria:
        productos = conn.execute(
            'SELECT * FROM productos WHERE categoria = ?', (categoria,)
        ).fetchall()
    else:
        productos = conn.execute('SELECT * FROM productos').fetchall()

    categorias = conn.execute(
        'SELECT DISTINCT categoria FROM productos ORDER BY categoria'
    ).fetchall()
    conn.close()

    return render_template('catalogo.html', productos=productos,
                           categorias=categorias, categoria_activa=categoria)


# ---------------------------------------------------------------
# BUSCADOR  ✅ SEGURO: PARÁMETROS EN CLÁUSULA LIKE
# ---------------------------------------------------------------
@app.route('/buscar')
def buscar():
    q = request.args.get('q', '').strip()

    if not q:
        return redirect(url_for('catalogo'))

    resultados = []
    pattern = f"%{q}%"
    query = (
        "SELECT * FROM productos "
        "WHERE nombre LIKE ? "
        "OR descripcion LIKE ? "
        "OR categoria LIKE ?"
    )

    conn = get_db()
    try:
        resultados = conn.execute(query, (pattern, pattern, pattern)).fetchall()
        conn.close()
    except Exception:
        conn.close()
        return render_template('error.html', error='No fue posible completar la búsqueda solicitada.')

    return render_template('buscar.html', resultados=resultados, q=q)


# ---------------------------------------------------------------
# DETALLE DE PRODUCTO  ✅ SEGURO: VALIDACIÓN DE TIPO Y PARÁMETROS
# ---------------------------------------------------------------
@app.route('/producto/<id>')
def producto(id):
    try:
        producto_id = int(id)
    except (ValueError, TypeError):
        return render_template('error.html', error='Identificador de producto inválido.')

    conn = get_db()
    try:
        query = "SELECT * FROM productos WHERE id = ?"
        p = conn.execute(query, (producto_id,)).fetchone()
        conn.close()
    except Exception:
        conn.close()
        return render_template('error.html', error='Error al recuperar la información del producto.')

    if not p:
        return render_template('error.html', error='Producto no encontrado.')

    return render_template('producto.html', producto=p)


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        from database import init_db
        init_db()
    app.run(debug=True)
