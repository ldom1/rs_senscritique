import datetime
from surprise import dump, Dataset, Reader, SlopeOne
from surprise.model_selection import GridSearchCV
import os
import pandas as pd
from tqdm import tqdm
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
import logging
import time
import json

from rssenscritique.config.global_variables import train_test_ratio, models_config
from rssenscritique.get_data_senscritique.scrapping.users_movies import agregate_users_movies_files, \
    get_one_user_movies

logging.basicConfig(level=logging.INFO)


def fit_model(model_name, model_config, trainset, data_train):
    start_time = time.time()

    logging.info(f'Recommendation System: Fit model - {model_name}')

    gs = GridSearchCV(model_config["model"],
                      model_config["params_grid"],
                      measures=['rmse', 'mae'],
                      cv=3,
                      n_jobs=-1,
                      joblib_verbose=0)

    gs.fit(data_train)
    logging.info(f'Recommendation System: Fit model - {model_name}: score = {gs.best_score}')
    model = model_config["model"](**gs.best_params['rmse'])
    model_fitted = model.fit(trainset)

    logging.info(f'Recommendation System: Fit model - {model_name} in {round(time.time() - start_time, 2)} s.')

    return model_fitted


def fit_slopeone(trainset):
    logging.info(f'Recommendation System: Fit model - SlopeOne')
    model = SlopeOne()
    model_fitted = model.fit(trainset)

    return model_fitted


def get_predictions(model, uid, iid):
    predictions = model.predict(uid=uid, iid=iid)
    uid, iid, r_ui, est, _ = predictions
    return est


def get_and_compare_predictions(df_test, model_fitted_dict):
    logging.info(f'Recommendation System: Compare models {list(model_fitted_dict.keys())}')

    res = {
        'model_name': [],
        'mse': [],
        'mae': [],
        'model': [],
        'score': [],
    }

    for name, model in tqdm(model_fitted_dict.items()):
        df_test['rating_predicted'] = df_test.apply(lambda row: get_predictions(model=model,
                                                                                uid=str(row['user_name']),
                                                                                iid=str(row['movie_name'])),
                                                    axis=1)

        mse = mean_squared_error(df_test.user_rating, df_test.rating_predicted)
        mae = mean_absolute_error(df_test.user_rating, df_test.rating_predicted)
        score = mse * mae

        res['model_name'].append(name)
        res['mse'].append(mse)
        res['mae'].append(mae)
        res['score'].append(score)
        res['model'].append(model)

    return pd.DataFrame(res)


def train_model():
    list_files = [y for y in os.listdir(GLOBAL_DATA_PATH + "users_movies/") if '.csv' in y]

    df = pd.concat([pd.read_csv(GLOBAL_DATA_PATH + "users_movies/" + y) for y in tqdm(list_files)])
    df = df.sample(frac=1)

    df = df[['user_name', 'movie_name', 'user_rating']]

    df = df.dropna()
    df['user_rating'] = df['user_rating'].astype(int)

    df_train = df.iloc[:int(train_test_ratio * df.shape[0])]
    df_test = df.iloc[int(train_test_ratio * df.shape[0]):]

    # reader class using only the rating parameter
    reader = Reader(rating_scale=(1, 10))

    # arranging dataframe
    data_train = Dataset.load_from_df(df_train, reader)

    # build full trainset and use cross validation for evaluation
    trainset = data_train.build_full_trainset()

    logging.info(f'Number of users:: {trainset.n_users}')
    logging.info(f'Number of items:: {trainset.n_items}')

    model_fitted_dict = {k: fit_model(model_name=k,
                                      model_config=v,
                                      trainset=trainset,
                                      data_train=data_train)
                         for k, v in models_config.items()}

    # model_fitted_dict['SlopeOne'] = fit_slopeone(trainset=trainset)

    df_compare_predictions = get_and_compare_predictions(df_test=df_test, model_fitted_dict=model_fitted_dict)

    best_model = df_compare_predictions[df_compare_predictions.score == np.min(df_compare_predictions.score)]

    metadata = {
        'model_name': best_model['model_name'].values[0],
        'mse': best_model['mse'].values[0],
        'mae': best_model['mae'].values[0]
    }

    logging.info(f'Training - best model: {metadata}')

    logging.info(f'Serializing model to: {MODEL_PATH}')
    try:
        dump.dump(file_name=MODEL_PATH,
                  algo=best_model['model'].values[0].fit(Dataset.load_from_df(df, reader).build_full_trainset()))
    except Exception as e:
        print(e)

    logging.info(f'Serializing metadata to: {METADATA_PATH}')
    try:
        with open(METADATA_PATH, 'w') as outfile:
            json.dump(metadata, outfile)
    except Exception as e:
        logging.info(f'Serializing metadata - ERROR: {e}')


try:
    GLOBAL_DATA_PATH = os.environ["GLOBAL_DATA_PATH"]
    MODEL_PATH = os.environ["MODEL_PATH"]
    METADATA_PATH = os.environ["METADATA_PATH"]
except Exception as e:
    print(e)
    GLOBAL_PATH = os.getcwd().replace("rssenscritique/recommended_system", "")
    GLOBAL_DATA_PATH = GLOBAL_PATH + 'data/'
    MODEL_PATH = GLOBAL_PATH + f'models/artefact/artefact_{datetime.datetime.today().strftime("%Y-%m-%d")}.joblib'
    METADATA_PATH = GLOBAL_PATH + f'models/metadata/metadata_{datetime.datetime.today().strftime("%Y-%m-%d")}.json'

user_name = 'l-giron-dom'
logging.info(f'Get last user movies: {user_name}')

# Either with csv or db
users = pd.read_csv(GLOBAL_DATA_PATH + "users/users.csv")
my_user = users[users.name == user_name]

get_one_user_movies(db_path=GLOBAL_DATA_PATH, user_name=user_name, user_url=my_user['url'], )

agregate_users_movies_files(db_path=GLOBAL_DATA_PATH)

logging.info(f'Train model on last data')
train_model()
