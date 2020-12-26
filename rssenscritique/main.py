import streamlit as st
import os
import pandas as pd
from surprise import dump
from tqdm import tqdm


def get_predictions(model, uid, iid):
    predictions = model.predict(uid=uid, iid=iid)
    uid, iid, r_ui, est, _ = predictions
    return est


def get_predicted_df(model_path, data_path):
    list_files = [y for y in os.listdir(data_path) if '.csv' in y]

    my_user_name = 'l-giron-dom'
    users_movies = pd.concat([pd.read_csv(data_path + y) for y in tqdm(list_files)])

    my_movies = users_movies[users_movies.user_name == my_user_name].movie_name
    users_movies = users_movies[~users_movies.movie_name.isin(my_movies)]
    df = pd.DataFrame({'movies': users_movies['movie_name'].unique()})

    model = dump.load(model_path)[1]

    df['prediction_rating'] = df['movies'].apply(lambda x: get_predictions(model=model,
                                                                           uid=my_user_name,
                                                                           iid=x))
    return df, my_user_name


st.write("""
# My recommendation system - [Sens critique](https://www.senscritique.com/)
""")

st.write("""
### Computing predictions ...
""")

try:
    STANDARD_PATH = os.getcwd().replace("rssenscritique", "")
    print(STANDARD_PATH)
    MODEL_PATH = STANDARD_PATH + "/models/artefact/artefact_2020-12-24.joblib"
    DATA_PATH = STANDARD_PATH + '/data/users_movies/'

    df, my_user_name = get_predicted_df(model_path=MODEL_PATH, data_path=DATA_PATH)

except FileNotFoundError as e:
    print(e)
    DATA_PATH = '/data/users_movies/'
    MODEL_PATH = '/models/artefact/artefact.joblib'

    df, my_user_name = get_predicted_df(model_path=MODEL_PATH, data_path=DATA_PATH)


st.write(f"Top 10 movies for you, {my_user_name}:")

st.dataframe(df.sort_values(by='prediction_rating', ascending=False).iloc[:10])
