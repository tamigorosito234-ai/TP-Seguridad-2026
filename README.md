# AfinAR — Plataforma Web de Instrumentos Musicales
### Trabajo Práctico Integrador (TPI) — Seguridad en el Desarrollo de Software (UTN FRC - 2026)

---

## 👥 Integrantes del Grupo

- **Giorgi, Lorenzo**
- **Franco, Martina**
- **Rojo, Roberto**
- **Gorosito, Tamara**
- **Crespin, Sasha**

---

## 📌 Descripción del Proyecto

**AfinAR** es una aplicación web de comercio electrónico desarrollada con **Python, Flask y SQLite** que simula un catálogo exclusivo de instrumentos musicales originales de fábrica y accesorios.

El objetivo de este proyecto es demostrar de forma práctica, aplicada y didáctica:
1. El impacto real de las vulnerabilidades de **Inyección SQL (SQLi)** en aplicaciones web.
2. La implementación rigurosa de controles de seguridad para mitigar el resto de los riesgos del **OWASP Top 10** (CSRF, XSS, IDOR, Clickjacking, Session Fixation).
3. La técnica estándar de la industria para resolver definitivamente SQLi mediante **Consultas Parametrizadas (Prepared Statements)**.

---

## 🌿 Estructura de Ramas del Repositorio

Para facilitar la evaluación docente y la exposición oral, el repositorio está dividido en dos ramas:

| Rama | Estado | Enfoque |
|---|---|---|
| **`main`** | ⚠️ **Vulnerable a SQLi** | Contiene las vulnerabilidades de SQL Injection intencionales, pero con **todas las demás capas de seguridad activas** (Anti-CSRF, Anti-XSS, Anti-IDOR, etc.). |
| **`secure`** | ✅ **100% Remediada** | Contiene el código corregido con **consultas preparadas** y validación de tipos, eliminando completamente la vulnerabilidad SQLi. |

```bash
# Alternar entre ramas:
git checkout main    # Versión para auditoría / demostración de vulnerabilidad
git checkout secure  # Versión remediada y segura
```

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

## 🔍 Análisis Detallado: ¿Qué Vulnerabilidades de SQLi se Dejaron en `main`?

> **Aclaración conceptual clave:** La vulnerabilidad **no reside en el motor de base de datos** (SQLite), sino en el **código de la aplicación**, específicamente en la construcción dinámica de sentencias SQL mediante **concatenación de cadenas (f-strings)** sin separación entre código y datos.

En la rama `main` se dejaron **3 parámetros vulnerables** en endpoints específicos:

```
+-----------------------------------------------------------------------------------+
|                              ARQUITECTURA DE DATOS                                |
|                                                                                   |
|   TABLA: 'usuarios'                          TABLA: 'productos'                   |
|   - id (INT, PK)                             - id (INT, PK)                       |
|   - username (TEXT, UNIQUE)                  - nombre (TEXT)                      |
|   - password (TEXT)                          - descripcion (TEXT)                 |
|   - email (TEXT)                             - categoria (TEXT)                   |
|   - rol (TEXT)                               - precio (REAL)                      |
|                                              - stock (INT)                        |
|                                              - imagen_url (TEXT)                  |
+-----------------------------------------------------------------------------------+
```

### 1. Endpoint: `POST /login` (Afecta tabla `usuarios`)
- **Parámetro vulnerable:** `username` (enviado por formulario POST).
- **Consulta en el código (`app.py`):**
  ```python
  query = f"SELECT * FROM usuarios WHERE username='{username}' AND password='{password}'"
  ```
- **Naturaleza del fallo:** **Bypass de Autenticación (Inyección en literal de texto)**.
- **Mecanismo:** Al concatenar directamente la entrada entre comillas simples `'`, un carácter de comilla cierra el delimitador de texto de SQL, permitiendo inyectar operadores lógicos y secuencias de comentario (`--`) que anulan por completo la verificación de la contraseña (`AND password=...`).

### 2. Endpoint: `GET /buscar?q=` (Afecta tabla `productos` y permite extraer `usuarios`)
- **Parámetro vulnerable:** `q` (enviado por parámetro URL en la query string).
- **Consulta en el código (`app.py`):**
  ```python
  query = f"SELECT * FROM productos WHERE nombre LIKE '%{q}%' OR descripcion LIKE '%{q}%' OR categoria LIKE '%{q}%'"
  ```
- **Naturaleza del fallo:** **Extracción de Datos mediante UNION (Cross-Table SQLi)**.
- **Mecanismo:** Aunque la consulta original consulta el catálogo de la tabla `productos`, la falta de saneamiento permite cerrar la cláusula `LIKE` e inyectar un operador `UNION SELECT`. Dado que ambas consultas operan sobre la misma base de datos, el atacante puede extraer registros de la tabla confidencial `usuarios` (nombres de usuario, correos, roles y contraseñas) y hacer que aparezcan reflejados en la interfaz del catálogo.

### 3. Endpoint: `GET /producto/<id>` (Afecta tabla `productos`)
- **Parámetro vulnerable:** `id` (pasado en la ruta de la URL).
- **Consulta en el código (`app.py`):**
  ```python
  query = f"SELECT * FROM productos WHERE id={id}"
  ```
- **Naturaleza del fallo:** **Inyección SQL en Literal Numérico (Integer-based SQLi)**.
- **Mecanismo:** A diferencia de los otros casos, aquí el parámetro **ni siquiera está delimitado por comillas**. Además, el backend no castea la entrada a entero (`int(id)`). Por ende, el atacante puede inyectar operadores booleanos directos (`OR 1=1`), subconsultas o sentencias de extracción sin necesidad de escapar comillas simples.

---

## 🔒 Comparación con la Solución en la Rama `secure`

En la rama `secure`, las 3 consultas anteriores fueron reemplazadas por **consultas preparadas (Prepared Statements)**:

| Endpoint | Código Vulnerable (`main`) | Código Seguro (`secure`) |
|---|---|---|
| **`/login`** | `f"WHERE username='{username}' AND password='{password}'"` | `"WHERE username = ? AND password = ?", (username, password)` |
| **`/buscar`** | `f"WHERE nombre LIKE '%{q}%' ..."` | `"WHERE nombre LIKE ? ...", (f"%{q}%", ...)` |
| **`/producto`** | `f"WHERE id={id}"` (sin validar tipo) | `producto_id = int(id)` + `"WHERE id = ?", (producto_id,)` |

> **Principio de Remediación:** Al utilizar marcadores de posición (`?`), el motor de la base de datos compila la estructura de la consulta antes de recibir los valores. Los datos del usuario se envían en un canal separado y se procesan **exclusivamente como valores literales**, imposibilitando que cualquier carácter especial altere la semántica de la consulta SQL.

---

## 🚀 Requisitos y Puesta en Marcha

### 1. Clonar el repositorio
```bash
git clone https://github.com/tamigorosito234-ai/TP-Seguridad-2026.git
cd TP-Seguridad-2026
```

### 2. Instalar dependencias
```bash
python -m pip install -r requirements.txt
```

### 3. Inicializar la base de datos local
```bash
python database.py
```

### 4. Ejecutar la aplicación
```bash
python app.py
```
Abrir en el navegador: **http://127.0.0.1:5000**
