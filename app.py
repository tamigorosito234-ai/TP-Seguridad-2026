from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'clave_super_secreta_tpi_2026'
DATABASE = 'afinar.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------
# INICIO
# ---------------------------------------------------------------
@app.route('/')
def index():
    return redirect(url_for('catalogo'))


# ---------------------------------------------------------------
# LOGIN  ⚠️ VULNERABLE A SQL INJECTION
#   Vulnerabilidad en backend (concatenación de entrada)
# ---------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # ⚠️ VULNERABLE: concatenación directa sin sanitizar
        query = f"SELECT * FROM usuarios WHERE username='{username}' AND password='{password}'"

        conn = get_db()
        try:
            user = conn.execute(query).fetchone()
            conn.close()
            if user:
                session['user'] = dict(user)
                return redirect(url_for('catalogo'))
            else:
                error = 'Usuario o contraseña incorrectos.'
        except Exception:
            conn.close()
            error = 'Error en la autenticación. Por favor, intente nuevamente.'

    return render_template('login.html', error=error)


# ---------------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


# ---------------------------------------------------------------
# CATÁLOGO
# ---------------------------------------------------------------
@app.route('/catalogo')
def catalogo():
    categoria = request.args.get('categoria', '')
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
# BUSCADOR  ⚠️ VULNERABLE A SQL INJECTION (UNION / extracción de datos)
# ---------------------------------------------------------------
@app.route('/buscar')
def buscar():
    q = request.args.get('q', '').strip()

    # Si se borra o se busca en blanco, vuelve al catálogo por defecto
    if not q:
        return redirect(url_for('catalogo'))

    resultados = []

    # ⚠️ VULNERABLE: concatenación directa en cláusula LIKE
    query = (
        f"SELECT * FROM productos "
        f"WHERE nombre LIKE '%{q}%' "
        f"OR descripcion LIKE '%{q}%' "
        f"OR categoria LIKE '%{q}%'"
    )

    conn = get_db()
    try:
        resultados = conn.execute(query).fetchall()
        conn.close()
    except Exception:
        conn.close()
        return render_template('error.html', error='No fue posible completar la búsqueda solicitada.')

    return render_template('buscar.html', resultados=resultados, q=q)


# ---------------------------------------------------------------
# DETALLE DE PRODUCTO  ⚠️ VULNERABLE A SQL INJECTION (basada en entero)
# ---------------------------------------------------------------
@app.route('/producto/<id>')
def producto(id):
    # ⚠️ VULNERABLE: id inyectable directamente en la consulta
    query = f"SELECT * FROM productos WHERE id={id}"

    conn = get_db()
    try:
        p = conn.execute(query).fetchone()
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
