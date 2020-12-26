import os
from surprise import SVD, KNNBasic, KNNWithMeans, KNNWithZScore, SVDpp, CoClustering

URSL_USERS_LIST = [f'https://www.senscritique.com/searchUser?p={i + 1}' for i in range(626)]

DB_PATH = os.getcwd().replace("get_data_senscritique/config", "data/") + "sens_critique_db.db"


def get_url_user_movie(user_name):
    return f'https://www.senscritique.com/{user_name}/collection/all/films/all/all/all/all/all/all/all/page-1'


STANDARD_HTML = """
    <!DOCTYPE html>
    <body>
    <p> STANDARD HTML </p>
    </body>
    </html>
"""

"""'SVDpp': {'model': SVDpp,
             'params_grid': {
                 'n_epochs': [10],
                 'lr_all': [0.007],
                 'reg_all': [0.02]
             }
             },
    'CoClustering': {'model': CoClustering,
                     'params_grid': {
                          'n_cltr_u': [3, 10, 20, 40, 60],
                          'n_cltr_i': [3, 10, 20, 40, 60],
                          'n_epochs': [5, 10, 15]
                      }
                      },
"""

models_config = {'SVD': {'model': SVD,
                         'params_grid': {
                             'n_epochs': [5, 10, 15],
                             'lr_all': [0.002, 0.005, 0.007],
                             'reg_all': [0.02, 0.4, 0.6]
                         }
                         },
                 'KNNBasic': {'model': KNNBasic,
                              'params_grid': {
                                  'k': [20, 40, 60],
                                  'min_k': [5, 10, 20]
                              }
                              },
                 'KNNWithMeans': {'model': KNNWithMeans,
                                  'params_grid': {
                                      'k': [20, 40, 60],
                                      'min_k': [5, 10, 20]
                                  }
                                  },
                 'KNNWithZScore': {'model': KNNWithZScore,
                                   'params_grid': {
                                       'k': [20, 40, 60],
                                       'min_k': [5, 10, 20]
                                   }
                                   },

                 }

train_test_ratio = 0.8
