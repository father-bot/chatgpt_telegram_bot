DOC_SOLACE = 'solace'
DOC_DT = 'dt'


def get_prompt(pregunta, doc=DOC_SOLACE):
    from utils_mateo import get_articulos_mencionados, get_articulos_by_embedding, encadena_articulos

    df = _carga_embedding(doc)  # carga el df con los embeddings de los artículos
    articulos_mencionados = get_articulos_mencionados(pregunta, df)
    articulos_by_embedding = get_articulos_by_embedding(pregunta, df, 4)
    articulos_str = encadena_articulos(articulos_mencionados+articulos_by_embedding, max_tokens=3500)

    prompt = _get_prompt(articulos_str)
    return prompt


def _get_prompt(articulos_str):
    prompt = f'Debes responder la pregunta del usuario basandote únicamente en el siguiente texto. Sólo si no encuentras ninguna respuesta en el texto, di "NO HAY INFORMACIÓN". Menciona los articulos en que te basas. El texto es el siguiente: {articulos_str}'

    return prompt


def _carga_embedding(doc):
    import pandas as pd
    import ast
    import re

    if doc == DOC_SOLACE:
        path = "bot/data_med/df_solace.csv"
    elif doc == DOC_DT:
        path = "bot/data_med/df_embedding_dt.csv"
    df = pd.read_csv(path)
    print(f'df cargado desde {path}')
    df['embedding'] = df['embedding'].apply(ast.literal_eval)
    df.rename(columns={'artículo': 'text'}, inplace=True)
    # agregamos la columna 'n_articulo' al df, con el número del artículo, que se obtiene de la columna 'text'. El texto empieza con 'Artículo {n}. ' donde n es el número del artículo
    df['n_articulo'] = df['text'].apply(lambda x: int(re.findall('\nartículo \d+', x.lower())[0].split(' ')[1]))

    return df
