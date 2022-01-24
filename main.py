import datetime
import pytz
import requests
import pandas as pd
from git import Repo


def rendFondo2022(nombreFondo:str, acotNombre:str):
    '''
    Esta función realiza una consulta al API de datos abiertos para traer inforamación de los rendimientos de los fondos de inversión.
    La función recibe el nombre del fondo y su acotación.
    Retorna el DF con una limpieza inicial y bajo la lógica de dos filtros. Fecha mayor a 31 de diciembre de 2021 y fondo número 803.
    '''
    url = f'https://www.datos.gov.co/resource/qhpu-8ixx.json?nombre_patrimonio={nombreFondo}&$limit=1500000'
    r = requests.get(url)
    data = r.json()
    df = pd.DataFrame(data)

    #TRANSFORMAR TIPO DE DATOS
    df['fecha_corte'] = pd.to_datetime(df['fecha_corte'])
    df['nombre_patrimonio'] = str(acotNombre)
    df = df.query("fecha_corte >'2021-12-31' and tipo_participacion=='803'")

    df = df.loc[:,['fecha_corte','nombre_patrimonio','rendimientos_abonados','numero_unidades_fondo_cierre','valor_unidad_operaciones','aportes_recibidos','retiros_redenciones','valor_fondo_cierre_dia_t','numero_inversionistas','rentabilidad_diaria','rentabilidad_mensual','rentabilidad_semestral','rentabilidad_anual']]
    df = df.loc[:,['fecha_corte','nombre_patrimonio','rentabilidad_diaria','rentabilidad_mensual','rentabilidad_semestral','rentabilidad_anual']]
    return df

# - Definimos los df de los fondos a consultar
df_alta_conviccion = rendFondo2022('FONDO DE INVERSION COLECTIVA ABIERTO RENTA ALTA CONVICCION', 'ALTA-CONVICCION')
df_sostenible_global = rendFondo2022('FONDO DE INVERSION COLECTIVA ABIERTO RENTA SOSTENIBLE GLOBAL', 'SOSTENIBLE-GLOBAL')

# - Concatenamos los dos df en uno solo
df_fondos_personales = pd.concat([df_alta_conviccion.sort_values('fecha_corte', ascending = False),df_sostenible_global.sort_values('fecha_corte', ascending = False)])
df_fondos_personales.reset_index(inplace=True)

# - cargamos JSON de de los LOGs
df_logAppend=pd.read_json('logAppend.json')
df_logTable=pd.read_json('logTable.json')

# - Calcular dias de ejecución
NOW = datetime.datetime.now(pytz.timezone('America/Bogota'))
EXECUTION_DATE = NOW.strftime("%Y-%m-%d %H:%M:%S")
EXECUTION_DATE_FN = NOW.strftime("%Y-%m-%d")

FECHA_BASE             = datetime.datetime.strptime(str(df_logTable.iloc[0]['fecha_base']), '%Y-%m-%d %H:%M:%S')
FECHA_ULTIMA_EJECUCION = datetime.datetime.strptime(str(df_logTable.iloc[0]['fecha_ultima_ejecucion']), '%Y-%m-%d %H:%M:%S')
TOTAL_DIAS_EJECUCION   = df_logTable.iloc[0]['total_dias_ejecucion']
TOTAL_PUSH             = df_logTable.iloc[0]['total_push']
TOTAL_PUSH_DIA         = df_logTable.iloc[0]['total_push_dia']

NEW_TOTAL_DIAS_EJECUCION =  (NOW.replace(tzinfo=None) - FECHA_BASE).days
NEW_TOTAL_PUSH = TOTAL_PUSH + 1

if FECHA_ULTIMA_EJECUCION.strftime("%Y-%m-%d")  == EXECUTION_DATE_FN:
    NEW_TOTAL_PUSH_DIA = TOTAL_PUSH_DIA + 1
else:
    NEW_TOTAL_PUSH_DIA = 1

# - Actualizar logTable.json
df_logTable['fecha_ultima_ejecucion'] = EXECUTION_DATE
df_logTable['total_dias_ejecucion'] = NEW_TOTAL_DIAS_EJECUCION
df_logTable['total_push'] = NEW_TOTAL_PUSH
df_logTable['total_push_dia'] = NEW_TOTAL_PUSH_DIA

df_logTable.to_json('logTable.json')

# - ActualizarlogAppend.json
df_logAppend = pd.concat([df_logAppend, df_logTable])
df_logAppend.reset_index(drop=True, inplace=True)
df_logAppend.to_json('logAppend.json')


# - Guardamos los resultado en el archivo README.md
with open("README.md", "w") as file:
    file.write('# automatización Rentabilidad Fondos Bancolombia\n')
    file.write('---')
    file.write('\n')
    file.write('## Resumen Ejecución Automática\n')
    file.write('---')
    file.write('\n')
    file.write(df_logTable.to_markdown())
    file.write('---')
    file.write('\n')
    file.write('## Rentabilidad último día consultado\n')
    file.write('---')
    file.write('\n')
    file.write(df_fondos_personales.sort_values('fecha_corte').tail(2).to_markdown())
    file.write('## Consolidado información 2022\n')
    file.write('---')
    file.write('\n')
    file.write(df_fondos_personales.to_markdown())
    file.write('\n')
    file.close()

PATH_OF_GIT_REPO = '/home/ec2-user/documentos/autRentabilidadFondos/.git'
COMMIT_MESSAGE = 'Commit Automatico EC2 Nro - ' + str(NEW_TOTAL_PUSH)

repo = Repo(PATH_OF_GIT_REPO)
repo.git.add('--all')
repo.index.commit(COMMIT_MESSAGE)
origin = repo.remote(name='origin')
origin.push().raise_if_error()
