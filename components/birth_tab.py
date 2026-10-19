from datetime import date
from nicegui import ui
from database.db import connect


def birth_section(on_change):
    ui.label('Partos y crías').classes('text-2xl font-bold')
    with ui.card().classes('w-full'):
        with ui.grid(columns=3).classes('w-full gap-3'):
            mother = ui.select(options={}, label='Madre')
            birth_date = ui.input('Fecha del parto', value=date.today().isoformat(), placeholder='AAAA-MM-DD')
            count = ui.number('Número de crías', min=1, value=1, precision=0)
            notes = ui.input('Notas')
        def load_mothers():
            with connect() as con:
                rows = con.execute("SELECT id,code,name FROM goats WHERE sex='Hembra' ORDER BY code").fetchall()
            mother.options = {r['id']: f"{r['code']} — {r['name']}" for r in rows}; mother.update()
        load_mothers()
        def save():
            if not mother.value or not birth_date.value:
                ui.notify('Selecciona una madre y una fecha.', type='warning'); return
            try:
                with connect() as con:
                    con.execute('INSERT INTO births(mother_id,birth_date,kids_count,notes) VALUES(?,?,?,?)',
                                (mother.value,birth_date.value,int(count.value or 1),notes.value or ''))
                notes.value=''; count.value=1; on_change(); ui.notify('Parto registrado.', type='positive')
            except Exception as exc: ui.notify(f'No se pudo guardar: {exc}', type='negative')
        ui.button('Guardar parto', icon='save', on_click=save).classes('bg-green-700 text-white')
    ui.separator()
    table = ui.table(columns=[
        {'name':'birth_date','label':'Fecha','field':'birth_date','sortable':True},
        {'name':'code','label':'Código madre','field':'code'}, {'name':'name','label':'Madre','field':'name'},
        {'name':'kids_count','label':'N.º crías','field':'kids_count'}, {'name':'notes','label':'Notas','field':'notes'}
    ], rows=[], row_key='id').classes('w-full')
    def load():
        with connect() as con:
            rows = con.execute('''SELECT b.id,b.birth_date,g.code,g.name,b.kids_count,b.notes
            FROM births b JOIN goats g ON g.id=b.mother_id ORDER BY b.birth_date DESC''').fetchall()
        table.rows = [dict(r) for r in rows]; table.update()
    on_change.register('births', load); load()
