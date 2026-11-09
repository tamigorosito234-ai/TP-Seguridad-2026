# AfinAR — Plataforma Web de Instrumentos Musicales
### Trabajo Práctico Integrador (TPI) — Seguridad en el Desarrollo de Software (UTN FRC - 2026)
### 🔒 Rama: `secure` (Versión Remediada)

---

## 📌 Estado de esta Rama: Remediada y Segura

Esta rama contiene la solución a todas las vulnerabilidades de **Inyección SQL (SQLi)** presentes en la rama `main`. Se implementó el estándar de la industria recomendado por **OWASP**: el uso de **Consultas Parametrizadas (Prepared Statements)** y la **Validación Estricta de Tipos**.

---

## 👥 Integrantes del Grupo

- **Giorgi, Lorenzo**
- **Franco, Martina**
- **Rojo, Roberto**
- **Gorosito, Tamara**
- **Crespin, Sasha**

---

## 🔄 Comparativa de Código: Vulnerable (`main`) vs Seguro (`secure`)

### 1. Inicio de Sesión (`/login`)

```diff
- # ⚠️ VULNERABLE (main): Concatenación directa de cadenas
- query = f"SELECT * FROM usuarios WHERE username='{username}' AND password='{password}'"
- user = conn.execute(query).fetchone()

+ # ✅ SEGURO (secure): Consulta parametrizada con placeholder '?'
+ query = "SELECT * FROM usuarios WHERE username = ? AND password = ?"
+ user = conn.execute(query, (username, password)).fetchone()
```
> **Fundamento:** El motor SQLite compila la estructura de la consulta de antemano. Los valores `username` y `password` se envían en un canal separado y se procesan exclusivamente como literales de texto. Aunque el atacante ingrese `' OR 1=1 --`, el motor buscará textualmente un usuario cuyo nombre sea esa cadena exacta.

---

### 2. Buscador (`/buscar?q=`)

```diff
- # ⚠️ VULNERABLE (main): Interpolación en la cláusula LIKE
- query = f"SELECT * FROM productos WHERE nombre LIKE '%{q}%' OR descripcion LIKE '%{q}%' OR categoria LIKE '%{q}%'"
- resultados = conn.execute(query).fetchall()

+ # ✅ SEGURO (secure): El comodín '%' se añade al parámetro en Python
+ pattern = f"%{q}%"
+ query = "SELECT * FROM productos WHERE nombre LIKE ? OR descripcion LIKE ? OR categoria LIKE ?"
+ resultados = conn.execute(query, (pattern, pattern, pattern)).fetchall()
```
> **Fundamento:** Evita la inyección de sentencias `UNION`, subconsultas y operadores booleanos. Cualquier carácter especial dentro de `q` es tratado como parte del texto de búsqueda.

---

### 3. Detalle de Producto (`/producto/<id>`)

```diff
- # ⚠️ VULNERABLE (main): Parámetro inyectado directamente
- query = f"SELECT * FROM productos WHERE id={id}"
- p = conn.execute(query).fetchone()

+ # ✅ SEGURO (secure): Validación de tipo entero + consulta parametrizada
+ try:
+     producto_id = int(id)
+ except (ValueError, TypeError):
+     return render_template('error.html', error='Identificador de producto inválido.')
+
+ query = "SELECT * FROM productos WHERE id = ?"
+ p = conn.execute(query, (producto_id,)).fetchone()
```
> **Fundamento:** Se aplica defensa en profundidad: validación de tipos previa (`int(id)`) y parametrización de la consulta.

---

## 🧪 Verificación de Remediación con SQLMap

Con la aplicación en ejecución (`python app.py`), se ejecutan las mismas pruebas de SQLMap que en la rama `main`:

### 1. Prueba en el buscador:
```bash
sqlmap -u "http://127.0.0.1:5000/buscar?q=guitarra" --batch
```
**Resultado esperado:**
> `[CRITICAL] all tested parameters do not appear to be injectable`

### 2. Prueba en el Login:
```bash
sqlmap -u "http://127.0.0.1:5000/login" --data="username=test&password=test" --method=POST --batch
```
**Resultado esperado:**
> `[WARNING] POST parameter 'username' does not seem to be injectable`

### 3. Prueba en el ID de Producto:
```bash
sqlmap -u "http://127.0.0.1:5000/producto/1" --batch
```
**Resultado esperado:**
> `[CRITICAL] all tested parameters do not appear to be injectable`

---

## 🔀 Volver a la versión vulnerable

Para alternar entre ramas:
```bash
# Cambiar a la versión vulnerable:
git checkout main

# Regresar a la versión segura:
git checkout secure
```
