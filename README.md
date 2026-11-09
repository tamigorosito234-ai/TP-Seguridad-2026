# AfinAR — Plataforma Web de Instrumentos Musicales
### Trabajo Práctico Integrador (TPI) — Seguridad en el Desarrollo de Software (UTN FRC - 2026)
### 🔒 Rama: `secure` (Versión 100% Remediada)

---

## 👥 Integrantes del Grupo

- **Giorgi, Lorenzo**
- **Franco, Martina**
- **Rojo, Roberto**
- **Gorosito, Tamara**
- **Crespin, Sasha**

---

## 📌 Estado de esta Rama: Remediada y Segura

Esta rama contiene la solución integral a todas las vulnerabilidades de **Inyección SQL (SQLi)** presentes en la rama `main`, combinada con la totalidad de los controles de seguridad implementados para el resto del **OWASP Top 10** (Anti-CSRF, Anti-XSS, Anti-IDOR, Anti-Clickjacking y Anti-Session Fixation).

Se implementó el estándar de la industria recomendado por **OWASP**: el uso riguroso de **Consultas Parametrizadas (Prepared Statements)** y la **Validación Estricta de Tipos de Entrada**.

---

## 🛡️ Informe de Seguridad: Funciones Implementadas en Ambas Ramas

Para garantizar que la aplicación no sea vulnerable a ninguna otra amenaza fuera del alcance pedagógico del TP, se desarrollaron e integraron los siguientes mecanismos de defensa en **ambas ramas**:

### 1. Protección contra CSRF (Cross-Site Request Forgery)
- **Generación de Tokens Criptográficos:** Se generan tokens aleatorios seguros de 256 bits (`secrets.token_hex(32)`) asociados a la sesión del usuario.
- **Validación Estricta en Métodos de Estado (`POST`):** El decorador `@app.before_request` intercepta cualquier solicitud `POST`. Si el token anti-CSRF no coincide con el de la sesión o no está presente, la petición es abortada inmediatamente con código HTTP `403 Forbidden`.
- **Cookies de Sesión Seguras:** Se configuró la directiva `SameSite=Lax`, impidiendo que navegadores envíen cookies de autenticación en solicitudes cross-site originadas por sitios externos.

### 2. Protección contra XSS (Cross-Site Scripting)
- **Autoescaping en Plantillas:** El motor Jinja2 escapa de forma predeterminada todos los caracteres de control HTML (`<`, `>`, `&`, `"`, `'`) en variables reflejadas (como búsquedas o errores).
- **Serialización Segura de Datos en DOM:** En los botones interactivos del carrito se utiliza el filtro `|tojson`, evitando que nombres de productos con apóstrofes o comillas puedan escapar de los atributos de JavaScript.
- **Content Security Policy (CSP):** Se implementó la cabecera `Content-Security-Policy` restringiendo la ejecución de recursos únicamente a fuentes autorizadas (`'self'`, Google Fonts y Unsplash).

### 3. Protección contra IDOR (Insecure Direct Object References)
- **Control de Acceso Basado en Sesión:** En la ruta `/perfil` (Mi Cuenta), la aplicación **no acepta identificadores de usuario por URL ni por parámetros manipulables** (como `/perfil?id=2` o `/perfil/2`).
- **Resolución en Servidor:** Los datos del perfil se consultan utilizando estrictamente el `session['user']['id']` verificado y firmado en la sesión del servidor. Ningún usuario puede visualizar información de otra cuenta alterando parámetros numéricos.

### 4. Protección contra Clickjacking
- Se añade la cabecera HTTP `X-Frame-Options: SAMEORIGIN` y la directiva CSP `frame-ancestors 'self'`, impidiendo que atacantes puedan embeber el sitio web dentro de marcos transparentes (`<iframe>`) para engañar al usuario.

### 5. Seguridad en Sesiones & Anti-MIME Sniffing
- **`SESSION_COOKIE_HTTPONLY = True`:** La cookie de sesión no puede ser leída mediante JavaScript (`document.cookie`), mitigando el robo de sesiones por XSS.
- **Anti-Session Fixation:** Cada vez que un usuario se autentica con éxito, la sesión previa se destruye completamente (`session.clear()`) y se genera un nuevo identificador de sesión y un nuevo token CSRF.
- **`X-Content-Type-Options: nosniff`:** Fuerza al navegador a respetar estrictamente los tipos MIME declarados, evitando ejecución de código malicioso camuflado en archivos estáticos.

---

## 🔄 Comparativa de Remediación: Vulnerable (`main`) vs Seguro (`secure`)

### 1. Inicio de Sesión (`POST /login` — Tabla `usuarios`)

```diff
- # ⚠️ VULNERABLE (main): Concatenación directa de cadenas (f-strings)
- query = f"SELECT * FROM usuarios WHERE username='{username}' AND password='{password}'"
- user = conn.execute(query).fetchone()

+ # ✅ SEGURO (secure): Consulta parametrizada con placeholder '?'
+ query = "SELECT * FROM usuarios WHERE username = ? AND password = ?"
+ user = conn.execute(query, (username, password)).fetchone()
```
> **Fundamento Técnico:** El motor SQLite compila y planifica la sintaxis de la consulta antes de enlazar los valores. Los parámetros `(username, password)` viajan por un canal desacoplado y son interpretados exclusivamente como cadenas de texto literales. Cualquier comilla simple `'`, operador lógico o comentario SQL es tratado como texto plano, imposibilitando el bypass de autenticación.

---

### 2. Buscador del Catálogo (`GET /buscar?q=` — Tabla `productos`)

```diff
- # ⚠️ VULNERABLE (main): Interpolación en la cláusula LIKE
- query = f"SELECT * FROM productos WHERE nombre LIKE '%{q}%' OR descripcion LIKE '%{q}%' OR categoria LIKE '%{q}%'"
- resultados = conn.execute(query).fetchall()

+ # ✅ SEGURO (secure): El comodín '%' se concatena al parámetro de datos en Python
+ pattern = f"%{q}%"
+ query = "SELECT * FROM productos WHERE nombre LIKE ? OR descripcion LIKE ? OR categoria LIKE ?"
+ resultados = conn.execute(query, (pattern, pattern, pattern)).fetchall()
```
> **Fundamento Técnico:** El comodín de búsqueda se construye dentro del valor de datos en Python (`pattern`), no en la estructura de la consulta SQL. Esto impide que un atacante cierre la consulta para encadenar sentencias `UNION SELECT` y extraer registros de la tabla `usuarios`.

---

### 3. Detalle de Producto (`GET /producto/<id>` — Tabla `productos`)

```diff
- # ⚠️ VULNERABLE (main): Parámetro numérico inyectado sin delimitadores ni casteo
- query = f"SELECT * FROM productos WHERE id={id}"
- p = conn.execute(query).fetchone()

+ # ✅ SEGURO (secure): Defensa en profundidad (Validación de tipo + Parametrización)
+ try:
+     producto_id = int(id)
+ except (ValueError, TypeError):
+     return render_template('error.html', error='Identificador de producto inválido.')
+
+ query = "SELECT * FROM productos WHERE id = ?"
+ p = conn.execute(query, (producto_id,)).fetchone()
```
> **Fundamento Técnico:** Se aplica validación estricta de tipos de entrada (*Type Checking*): si el parámetro contiene caracteres no enteros, la petición se rechaza de inmediato sin tocar la base de datos. Además, la consulta se parametriza con `?`, garantizando que solo un entero sea procesado.

---

## 🔀 Alternar entre Versiones

```bash
# Cambiar a la versión vulnerable para demostración:
git checkout main

# Regresar a la versión segura:
git checkout secure
```
