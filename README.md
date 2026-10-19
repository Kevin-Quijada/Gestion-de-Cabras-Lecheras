# Gestión de cabras — NiceGUI

Aplicación local de gestión del rebaño con una interfaz moderna, componentes separados y base de datos SQLite.

## Instalar
En la terminal de VS Code, dentro de esta carpeta:

```bash
python -m pip install -r requirements.txt
```

## Ejecutar

```bash
python main.py
```

Después abre http://127.0.0.1:8080 si el navegador no se abre solo.

## Funciones
- Registrar cabras con código, nombre, sexo, raza, nacimiento, color, peso, estado y progenitores.
- Registrar producción diaria de leche por cabra; repetir cabra y fecha actualiza el registro existente.
- Registrar partos y número de crías.
- Consultar los progenitores en la pestaña de genealogía.
- Exportar CSV compatibles con Excel en `~/GestionCabras/exportaciones`.

## Archivos
- `main.py`: página principal, navegación, resumen y exportación.
- `database/db.py`: conexión y estructura SQLite.
- `components/`: una sección de interfaz por archivo.

La base de datos está en `~/GestionCabras/rebanio.db`. Si ya usabas una versión anterior, haz una copia de seguridad antes de ejecutar. Esta versión espera que las tablas `goats`, `milk` y `births` tengan la estructura indicada en `database/db.py`.
