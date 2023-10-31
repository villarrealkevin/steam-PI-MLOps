
# Proyecto Individual Machine Learning Operations

<p align="center">
    <img src="https://user-images.githubusercontent.com/67664604/217914153-1eb00e25-ac08-4dfa-aaf8-53c09038f082.png" alt="imagen">
</p>

#### En este proyecto se lleva a cabo el rol de un Data Scientist en Steam, se nos facilitan 3 datasets en formato ".json.gz" a partir de los cuales deberemos realizar 5 Endpoints en una API deployada en Render, asi como un Endpoint adicional para un sistema de recomendacion.

## ETL

### archivo de games:
- Extraccion de datos
- Control de nulos (eliminacion general)
- Control de columnas (eliminacion selectiva)
- Control de duplicados (columna "app_name")
- Transformaciones en la columna "release_date", eliminacion de valores como "SOON" o "SOON™", transformacion de fechas irregulares, extraccion del año y transformacion a tipo "int"
- Transformaciones en la columna "price", transformacion a tipo "float" en caso de ser posible, en caso de que no sea posible se asigna el valor 0
- Transformaciones en la columna "id", transformacion a tipo "int"
- Se guarda en CSV con el nombre "df_games"

### archivo de reviews:
- Extraccion de datos
- Control de columnas (eliminacion selectiva)
- Desanidado de diccionario en formato json, resultado separado del dataframe original
- Analisis de sentimiento
- Se guarda en CSV con el nombre "df_reviews_desanidado" uniendo el dataframe original con el dataframe desanidado

### archivo de items:
- Extraccion de datos
- Control de columnas (eliminacion selectiva)
- Control de duplicados (columna "user_id")
- Desanidado de diccionario en formato json, resultado separado del dataframe original
- Se guarda el dataframe original sin la columna desanidada en CSV con el nombre "df_items"
- Transformaciones en la columna "item_id" del dataframe desanidado, transformacion a tipo "int"
- Control de columnas dataframe desanidado (eliminacion selectiva)
- se guarda el dataframe desanidado en Parquet con compresion "SNAPPY"

## EDA