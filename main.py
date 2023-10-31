from fastapi import FastAPI
from sklearn.neighbors import NearestNeighbors
import pandas as pd

df_games = pd.read_csv("post_ETL/df_games.csv")
games_ml = pd.read_csv("post_ETL/df_games_ml.csv")
df_items = pd.read_csv("post_ETL/df_items.csv")
df_reviews_desanidado = pd.read_csv("post_ETL/df_reviews_desanidado.csv")
df_items_desanidado = pd.read_parquet("post_ETL/df_items_desanidado.parquet")

k = 5
model = NearestNeighbors(n_neighbors=k, metric='euclidean')
model.fit(games_ml)

app = FastAPI()

@app.get("/developer/{desarrollador}")
def developer(desarrollador):
    desarrollador_sin_comillas = desarrollador.replace('"', "")
    df_games_filtrado = df_games[df_games["developer"].str.replace('"', '') == desarrollador_sin_comillas]
    años_conteo = df_games_filtrado["release_date"].value_counts()
    años_conteo = años_conteo.sort_index()
    resultados = []
    for year, count in años_conteo.items():
        juegos_por_año = df_games_filtrado[df_games_filtrado["release_date"] == year]
        juegos_gratuitos = juegos_por_año[juegos_por_año["price"] == 0]["price"].count()
        porcentaje_gratuitos = (juegos_gratuitos  * 100) / count
        resultados.append({"Año": str(year), "Cantidad de Items": count, "Contenido Free": "{}%".format(porcentaje_gratuitos)})
    return resultados

@app.get("/userdata/{user_id}")
def userdata(user_id):
    cantidad = df_items["items_count"][df_items["user_id"] == user_id]
    reviews_filtrado = df_reviews_desanidado[df_reviews_desanidado["user_id"] == user_id]
    conteo_total = len(reviews_filtrado)
    conteo_true = len(reviews_filtrado[reviews_filtrado["recommend"] == True])
    if conteo_total == 0:
        porcentaje_recommend = 0
    else:
        porcentaje_recommend = (conteo_true * 100) / conteo_total
    indice = df_items.index[df_items["user_id"] == user_id].tolist()
    if indice:
        juegos = df_items_desanidado["item_id"][df_items_desanidado["row_index"] == indice[0]]
    else:
        juegos = []
    games_filtrado = df_games[df_games["id"].isin(juegos)]
    dinero_gastado = games_filtrado["price"].sum()
    resultado = []
    resultado.append({"items": cantidad.tolist(), "% de recomendacion": "{}%".format(porcentaje_recommend), "dinero gastado": "{:.2f}".format(dinero_gastado)})
    return resultado

@app.get("/UserForGenre/{genero}")
def UserForGenre(genero):
    juegos = df_games[df_games["genres"].str.contains(genero)]["id"]
    games_filtrado = df_games[df_games["genres"].str.contains(genero)]
    items_filtrado = df_items_desanidado[df_items_desanidado["item_id"].isin(juegos)]
    playtime = items_filtrado.groupby("row_index")["playtime_forever"].sum()
    playtime_id = items_filtrado.groupby("item_id")["playtime_forever"].sum()
    juegos_con_horas = games_filtrado.merge(playtime_id, left_on="id", right_index=True)
    horas_año = juegos_con_horas.groupby(["release_date"])["playtime_forever"].sum().reset_index()
    horas_año = horas_año.set_index("release_date")
    usuario_mayor = playtime.idxmax()
    usuario = df_items.iloc[usuario_mayor]["user_id"]
    resultado = []
    resultado.append({f"Usuario con mas horas jugadas para genero {genero}": usuario, "Horas jugadas": horas_año.to_dict()})
    return resultado
    
@app.get("/best_develope_year/")
def best_developer_year(año):
    games_filtrado = df_games[df_games["release_date"] == int(año)]
    juegos_developer = pd.DataFrame(games_filtrado.groupby(["developer"])["id"].unique())
    juegos_developer = juegos_developer.explode("id")
    juegos_developer = juegos_developer.reset_index()
    total = juegos_developer.merge(df_reviews_desanidado, left_on="id", right_on="item_id")
    total_filtrado = total[total["recommend"] == True]
    recomendaciones = total_filtrado.groupby(["developer"]).agg({"recommend": "count", "sentiment_analysis": lambda x: (x == 2).sum()})
    recomendaciones = recomendaciones.sort_values(by=["recommend"], ascending=False)
    top_3 = [{"Puesto 1": recomendaciones.index[0]}, {"Puesto 2": recomendaciones.index[1]}, {"Puesto 3": recomendaciones.index[2]}]
    return top_3

@app.get("/developer_reviews_analysis/")
def developer_reviews_analysis(desarrolladora):
    games_filtrado = df_games[df_games["developer"] == desarrolladora]
    juegos_id = games_filtrado["id"]
    reviews_filtrado = df_reviews_desanidado[df_reviews_desanidado["item_id"].isin(juegos_id)]
    positivo = reviews_filtrado[reviews_filtrado["sentiment_analysis"] == 2]["sentiment_analysis"].count()
    negativo = reviews_filtrado[reviews_filtrado["sentiment_analysis"] == 0]["sentiment_analysis"].count()
    resultado = {desarrolladora: {"Negative": int(negativo), "Positive": int(positivo)}}
    return resultado

@app.get("/recomendacion_juego/")
def recommend_games(id):
    k = 5
    juego_filtrado = df_games[df_games["id"] == int(id)]
    indice = juego_filtrado.index
    game_ml_input = games_ml.loc[indice].values.reshape(1, -1)
    distances, indices = model.kneighbors(game_ml_input, n_neighbors=k + 1)
    recommended_games = games_ml.iloc[indices[0][1:]]
    indice2 = recommended_games.index
    recomendacion_filtrada = df_games.iloc[indice2]
    lista = recomendacion_filtrada["app_name"].tolist()
    return lista