from nicegui import ui
from pathlib import Path
import csv
from database.db import init_db, connect, DB_PATH
from components.goats_tab import goats_section
from components.milk_tab import milk_section
from components.birth_tab import birth_section
from components.family_tab import family_section

init_db()

class Refresher:
    def __init__(self): self.loaders = {}
    def register(self, name, fn): self.loaders[name] = fn
    def __call__(self):
        for fn in list(self.loaders.values()): fn()
        update_summary()
refresh = Refresher()
summary_total = None
summary_active = None

def update_summary():
    global summary_total, summary_active
    with connect() as con:
        row = con.execute("SELECT COUNT(*) total, COALESCE(SUM(CASE WHEN status='Activa' THEN 1 ELSE 0 END),0) active FROM goats").fetchone()
    if summary_total is not None: summary_total.text = str(row['total'])
    if summary_active is not None: summary_active.text = str(row['active'])

def export_csv():
    folder = Path.home() / 'GestionCabras' / 'exportaciones'
    folder.mkdir(parents=True, exist_ok=True)
    queries = {
        'cabras.csv': 'SELECT code,name,sex,breed,birth_date,color,weight_kg,status,notes FROM goats ORDER BY code',
        'produccion_leche.csv': '''SELECT g.code,g.name,m.record_date,m.morning_l,m.evening_l,(m.morning_l+m.evening_l) total_l,m.notes FROM milk m JOIN goats g ON g.id=m.goat_id ORDER BY m.record_date DESC''',
        'partos.csv': '''SELECT g.code madre_codigo,g.name madre,b.birth_date,b.kids_count,b.notes FROM births b JOIN goats g ON g.id=b.mother_id ORDER BY b.birth_date DESC''',
    }
    with connect() as con:
        for filename, query in queries.items():
            rows = con.execute(query).fetchall()
            with (folder / filename).open('w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                if rows:
                    writer.writerow(rows[0].keys())
                    writer.writerows([tuple(r) for r in rows])
    ui.notify(f'CSV exportados en {folder}', type='positive')

@ui.page('/')
def home():
    global summary_total, summary_active
    ui.colors(primary='#166534', secondary='#64748b', accent='#84cc16')
    with ui.header().classes('items-center justify-between bg-green-800 text-white'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('pets', size='2rem')
            with ui.column().classes('gap-0'):
                ui.label('Gestión de cabras').classes('text-xl font-bold')
                ui.label('Rebaño · leche · partos · genealogía').classes('text-sm opacity-80')
        ui.button('Exportar CSV', icon='download', on_click=export_csv).props('flat color=white')
    with ui.column().classes('w-full max-w-7xl mx-auto p-4 gap-4'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('Resumen del rebaño').classes('text-2xl font-bold')
            ui.button('Actualizar', icon='refresh', on_click=lambda: (refresh(), ui.notify('Datos actualizados')))
        with ui.grid(columns=3).classes('w-full'):
            with ui.card().classes('w-full'):
                ui.label('Cabras registradas').classes('text-gray-500'); summary_total = ui.label('0').classes('text-3xl font-bold')
            with ui.card().classes('w-full'):
                ui.label('Cabras activas').classes('text-gray-500'); summary_active = ui.label('0').classes('text-3xl font-bold')
            with ui.card().classes('w-full'):
                ui.label('Base de datos').classes('text-gray-500'); ui.label(str(DB_PATH)).classes('text-sm break-all')
        with ui.tabs().classes('w-full') as tabs:
            t_goats = ui.tab('Cabras', icon='pets')
            t_milk = ui.tab('Producción de leche', icon='water_drop')
            t_births = ui.tab('Partos y crías', icon='child_friendly')
            t_family = ui.tab('Árbol genealógico', icon='account_tree')
        with ui.tab_panels(tabs, value=t_goats).classes('w-full'):
            with ui.tab_panel(t_goats): goats_section(refresh)
            with ui.tab_panel(t_milk): milk_section(refresh)
            with ui.tab_panel(t_births): birth_section(refresh)
            with ui.tab_panel(t_family): family_section()
        update_summary()

ui.run(title='Gestión de cabras', reload=False, port=8080)
