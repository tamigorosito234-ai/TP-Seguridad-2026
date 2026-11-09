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
# LOGIN  ✅ REMEDIADO CON CONSULTAS PARAMETRIZADAS (PREPARED STATEMENTS)
#   Los valores de 'username' y 'password' se pasan como parámetros tupla.
#   El motor de base de datos los trata estrictamente como datos literales,
#   impidiendo que caracteres como ' o -- alteren la sintaxis SQL.
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
    categoria = request.args.get('categoria', '').strip()
    conn = get_db()
    if categoria:
        # ✅ SEGURO: Consulta parametrizada
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
# BUSCADOR  ✅ REMEDIADO CON PARÁMETROS EN CLÁUSULA LIKE
#   El comodín '%' se concatena al parámetro de datos en Python,
#   no dentro de la consulta SQL. La base de datos recibe los datos
#   de forma aislada, evitando inyecciones de tipo UNION o Blind.
# ---------------------------------------------------------------
@app.route('/buscar')
def buscar():
    q = request.args.get('q', '').strip()

    if not q:
        return redirect(url_for('catalogo'))

    resultados = []
    # ✅ SEGURO: El patrón se arma en el valor, no en la estructura de la consulta
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
# DETALLE DE PRODUCTO  ✅ REMEDIADO CON VALIDACIÓN DE TIPO Y PARÁMETROS
#   1. Se valida que el id sea estrictamente numérico (int).
#   2. Se pasa el id sanitizado como parámetro posicional '?'.
# ---------------------------------------------------------------
@app.route('/producto/<id>')
def producto(id):
    # ✅ SEGURO: Validación de tipo (Type Checking)
    try:
        producto_id = int(id)
    except (ValueError, TypeError):
        return render_template('error.html', error='Identificador de producto inválido.')

    conn = get_db()
    try:
        # ✅ SEGURO: Consulta parametrizada
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
