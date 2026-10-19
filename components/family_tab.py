from nicegui import ui
from database.db import connect


def family_section():
    ui.label('Árbol genealógico').classes('text-2xl font-bold')
    ui.label('Consulta los progenitores que hayas registrado para cada animal.').classes('text-gray-600')
    with connect() as con:
        goats = con.execute('SELECT id,code,name FROM goats ORDER BY code').fetchall()
    selector = ui.select(options={r['id']:f"{r['code']} — {r['name']}" for r in goats}, label='Cabra', clearable=True).classes('w-full max-w-xl')
    result = ui.column().classes('w-full')
    def show():
        result.clear()
        if not selector.value:
            with result: ui.label('Elige una cabra.').classes('text-gray-500')
            return
        with connect() as con:
            r = con.execute('''SELECT g.code,g.name,g.sex,g.breed,g.birth_date,
            m.code mother_code,m.name mother_name,f.code father_code,f.name father_name
            FROM goats g LEFT JOIN goats m ON g.mother_id=m.id LEFT JOIN goats f ON g.father_id=f.id
            WHERE g.id=?''',(selector.value,)).fetchone()
        with result:
            with ui.card().classes('w-full max-w-xl'):
                ui.label(f"{r['code']} — {r['name']}").classes('text-xl font-bold')
                ui.label(f"Sexo: {r['sex']} · Raza: {r['breed'] or 'No indicada'}")
                ui.label(f"Nacimiento: {r['birth_date'] or 'No indicado'}")
                ui.label(f"Madre: {r['mother_code']+' — '+r['mother_name'] if r['mother_code'] else 'No registrada'}")
                ui.label(f"Padre: {r['father_code']+' — '+r['father_name'] if r['father_code'] else 'No registrado'}")
    selector.on_value_change(lambda _: show()); show()
