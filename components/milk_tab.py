from datetime import date
from nicegui import ui
from database.db import connect


def milk_section(on_change):
    ui.label('Producción de leche').classes('text-2xl font-bold')
    ui.label('Un registro por cabra y día. Si guardas la misma fecha otra vez, se actualiza.').classes('text-gray-600')
    with ui.card().classes('w-full'):
        with ui.grid(columns=3).classes('w-full gap-3'):
            goat = ui.select(options={}, label='Cabra')
            record_date = ui.input('Fecha *', value=date.today().isoformat(), placeholder='AAAA-MM-DD')
            morning = ui.number('Mañana (L)', min=0, value=0, format='%.2f')
            evening = ui.number('Tarde (L)', min=0, value=0, format='%.2f')
            notes = ui.input('Notas')
        def load_goats():
            with connect() as con:
                rows = con.execute("SELECT id,code,name FROM goats WHERE sex='Hembra' ORDER BY code").fetchall()
            goat.options = {r['id']: f"{r['code']} — {r['name']}" for r in rows}; goat.update()
        load_goats()
        def save():
            if not goat.value or not record_date.value:
                ui.notify('Selecciona una cabra y una fecha.', type='warning'); return
            try:
                with connect() as con:
                    con.execute('''INSERT INTO milk(goat_id,record_date,morning_l,evening_l,notes) VALUES(?,?,?,?,?)
                    ON CONFLICT(goat_id,record_date) DO UPDATE SET morning_l=excluded.morning_l,
                    evening_l=excluded.evening_l,notes=excluded.notes''',
                    (goat.value, record_date.value, morning.value or 0, evening.value or 0, notes.value or ''))
                notes.value = ''; on_change(); ui.notify('Producción guardada.', type='positive')
            except Exception as exc: ui.notify(f'No se pudo guardar: {exc}', type='negative')
        ui.button('Guardar producción', icon='save', on_click=save).classes('bg-green-700 text-white')
    ui.separator()
    table = ui.table(columns=[
        {'name':'record_date','label':'Fecha','field':'record_date','sortable':True},
        {'name':'code','label':'Código','field':'code'}, {'name':'name','label':'Cabra','field':'name'},
        {'name':'morning_l','label':'Mañana (L)','field':'morning_l'}, {'name':'evening_l','label':'Tarde (L)','field':'evening_l'},
        {'name':'total','label':'Total (L)','field':'total'}, {'name':'notes','label':'Notas','field':'notes'}
    ], rows=[], row_key='id').classes('w-full')
    def load():
        with connect() as con:
            rows = con.execute('''SELECT m.id,m.record_date,g.code,g.name,m.morning_l,m.evening_l,
            ROUND(m.morning_l+m.evening_l,2) total,m.notes FROM milk m JOIN goats g ON g.id=m.goat_id
            ORDER BY m.record_date DESC,g.code''').fetchall()
        table.rows = [dict(r) for r in rows]; table.update()
    on_change.register('milk', load); load()
