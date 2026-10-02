# Mimi, plataforma de videos

Aplicación SPA modular para la actividad de Cloud. En desarrollo usa React + Vite, FastAPI, SQLAlchemy, SQLite y almacenamiento local de archivos. La configuración permite cambiar a PostgreSQL y Amazon S3 sin incluir credenciales en el código.

## Requisitos

- Node.js 20 o superior y npm.
- Python 3.11 o superior.

## Inicio local

Abre dos terminales en la carpeta raíz.

Terminal 1, API:

```powershell
py -m venv .venv
\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item backend\.env.example backend\.env
\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --app-dir .
```

La API y documentación quedan en `http://localhost:8000` y `http://localhost:8000/docs`. SQLite crea `frame.db` y los archivos se guardan en `backend/uploads/` por defecto.

Terminal 2, frontend:

```powershell
npm.cmd install
Copy-Item .env.example .env
npm.cmd run dev
```

Abre `http://localhost:5173`. Si tu PowerShell permite scripts npm, también puedes usar `npm` en lugar de `npm.cmd`.

Para probar registro, login, publicación, permisos, comentarios, edición y borrado contra SQLite en memoria:

```powershell
\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
\.venv\Scripts\python.exe -m pytest
```

## Funcionalidad

- Registro, inicio de sesión y token Bearer con contraseñas derivadas con scrypt.
- Catálogo con búsqueda, miniaturas, creador, vistas y fecha.
- Reproducción MP4, comentarios y recomendaciones desde la API.
- Perfil con conteos, publicación MP4 (máximo 100 MB), miniatura JPG/JPEG/PNG (máximo 10 MB), edición y eliminación propias.
- API documentada en `/docs`; archivos binarios separados de los metadatos relacionales.

## Configuración y transición a AWS

`backend/.env.example` documenta las variables. `DATABASE_URL` acepta SQLite local o una URL PostgreSQL para RDS. Para S3, configura `AWS_REGION`, `S3_VIDEO_BUCKET` y `S3_THUMBNAIL_BUCKET`; el SDK usa la cadena estándar de credenciales y, en EC2, debe recibir permisos mediante un IAM Role. Sin URL pública configurada, la API firma URLs de medios privadas al responder. No guardes claves AWS ni secretos en Git. Antes de desplegar cambia `SECRET_KEY`, restringe `CORS_ORIGINS` al dominio real y usa HTTPS.

El adaptador `backend/app/storage.py` elige almacenamiento local o S3 según la configuración. Los buckets de objetos necesitan una política adecuada para servir medios; no actives acceso público indiscriminadamente. Configura `S3_PUBLIC_BASE_URL` con un dominio/CDN autorizado o implementa URLs firmadas de corta duración antes de producción. La aplicación no crea recursos AWS automáticamente.

Para compilar la SPA ejecuta `npm.cmd run build`. Sube **únicamente el contenido de `dist/`** al bucket S3 del frontend. No subas `src/`, `node_modules/`, `package.json`, `.env`, la base SQLite ni archivos de usuario. Configura el hosting/CDN con fallback de rutas a `index.html`, HTTPS y la variable `VITE_API_URL` apuntando a la API desplegada antes de compilar.

## GitHub

```powershell
git add .
git commit -m "Build local video platform"
git branch -M main
git remote add origin https://github.com/USUARIO/REPOSITORIO.git
git push -u origin main
```

Revisa `git status` antes de publicar y confirma que `.env`, `backend/.env`, `*.db`, `backend/uploads/`, `node_modules/` y `dist/` no estén incluidos. El `.gitignore` ya los excluye.

## Estructura

```text
src/                    SPA React, pantallas y componentes
backend/app/             API FastAPI, configuración, modelos y rutas
backend/app/storage.py   Adaptador para disco local y S3
requirements.txt         Dependencias Python
```
