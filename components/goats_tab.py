from nicegui import ui
from database.db import connect


def goats_section(on_change):
    ui.label('Registro de cabras').classes('text-2xl font-bold')
    ui.label('Registra los animales y consulta el estado del rebaño.').classes('text-gray-600')
    with ui.card().classes('w-full'):
        ui.label('Nueva cabra').classes('text-lg font-semibold')
        with ui.grid(columns=3).classes('w-full gap-3'):
            code = ui.input('Código *', placeholder='Ej. C-001')
            name = ui.input('Nombre *', placeholder='Ej. Luna')
            sex = ui.select(['Hembra', 'Macho'], value='Hembra', label='Sexo')
            breed = ui.input('Raza', placeholder='Ej. Alpina')
            birth_date = ui.input('Nacimiento', placeholder='AAAA-MM-DD')
            color = ui.input('Color', placeholder='Ej. blanca y marrón')
            weight = ui.number('Peso (kg)', min=0, format='%.2f')
            status = ui.select(['Activa', 'Vendida', 'Fallecida', 'Inactiva'], value='Activa', label='Estado')
            notes = ui.input('Notas', placeholder='Observaciones')
            mother = ui.select(options={}, label='Madre (opcional)', clearable=True)
            father = ui.select(options={}, label='Padre (opcional)', clearable=True)

        def load_parents():
            with connect() as con:
                rows = con.execute('SELECT id, code, name FROM goats ORDER BY code').fetchall()
            opts = {r['id']: f"{r['code']} — {r['name']}" for r in rows}
            mother.options, father.options = opts, opts
            mother.update(); father.update()
        load_parents()

        def save():
            if not (code.value or '').strip() or not (name.value or '').strip():
                ui.notify('Completa el código y el nombre.', type='warning'); return
            try:
                with connect() as con:
                    con.execute('''INSERT INTO goats
                    (code,name,sex,breed,birth_date,color,weight_kg,status,mother_id,father_id,notes)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                    (code.value.strip(), name.value.strip(), sex.value, breed.value or '', birth_date.value or '',
                     color.value or '', weight.value, status.value, mother.value, father.value, notes.value or ''))
                for field in (code, name, breed, birth_date, color, notes): field.value = ''
                weight.value = None; sex.value = 'Hembra'; status.value = 'Activa'; mother.value = None; father.value = None
                load_parents(); on_change(); ui.notify('Cabra guardada.', type='positive')
            except Exception as exc:
                ui.notify(f'No se pudo guardar: {exc}', type='negative')
        ui.button('Guardar cabra', icon='save', on_click=save).classes('bg-green-700 text-white')

    ui.separator()
    ui.label('Cabras registradas').classes('text-xl font-semibold')
    table = ui.table(columns=[
        {'name':'code','label':'Código','field':'code','sortable':True},
        {'name':'name','label':'Nombre','field':'name','sortable':True},
        {'name':'sex','label':'Sexo','field':'sex'}, {'name':'breed','label':'Raza','field':'breed'},
        {'name':'birth_date','label':'Nacimiento','field':'birth_date'},
        {'name':'weight_kg','label':'Peso kg','field':'weight_kg'}, {'name':'status','label':'Estado','field':'status'}
    ], rows=[], row_key='id').classes('w-full')
    def load():
        with connect() as con:
            rows = con.execute('SELECT id,code,name,sex,breed,birth_date,weight_kg,status FROM goats ORDER BY code').fetchall()
        table.rows = [dict(r) for r in rows]; table.update()
    on_change.register('goats', load)
    load()
