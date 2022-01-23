import requests
import pandas as pd


def rendFondo2022(nombreFondo:str, acotNombre:str):
  url = f'https://www.datos.gov.co/resource/qhpu-8ixx.json?nombre_patrimonio={nombreFondo}&$limit=1500000'
  r = requests.get(url)
  data = r.json()
  df = pd.DataFrame(data)

  #TRANSFORMAR TIPO DE DATOS
  df['fecha_corte'] = pd.to_datetime(df['fecha_corte'])
  df['nombre_patrimonio'] = str(acotNombre)
  df = df.query("fecha_corte >'2021-12-31' and tipo_participacion=='803'")

  df = df.loc[:,['fecha_corte','nombre_patrimonio','rendimientos_abonados',
          'numero_unidades_fondo_cierre','valor_unidad_operaciones',
          'aportes_recibidos','retiros_redenciones','valor_fondo_cierre_dia_t','numero_inversionistas',
          'rentabilidad_diaria','rentabilidad_mensual','rentabilidad_semestral','rentabilidad_anual']]

  df = df.loc[:,['fecha_corte','nombre_patrimonio','rentabilidad_diaria','rentabilidad_mensual','rentabilidad_semestral','rentabilidad_anual']]
  return df

  
df_alta_conviccion = rendFondo2022('FONDO DE INVERSION COLECTIVA ABIERTO RENTA ALTA CONVICCION', 'ALTA-CONVICCION')
df_sostenible_global = rendFondo2022('FONDO DE INVERSION COLECTIVA ABIERTO RENTA SOSTENIBLE GLOBAL', 'SOSTENIBLE-GLOBAL')

df_fondos_personales = pd.concat([df_alta_conviccion.sort_values('fecha_corte', ascending = False),df_sostenible_global.sort_values('fecha_corte', ascending = False)])
with open("README.md", "a") as o:
    o.write('# autRentabilidadFondos\n ')
    o.write('Automatización rentablidad de fondos de inversión de Valores Bancolombia -Alta Convicción y Sostenible Global- con información de datos abiertos.\n')
    o.write(df_fondos_personales.to_markdown())