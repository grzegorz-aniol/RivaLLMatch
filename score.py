from typing import List, Dict
import json
import numpy as np
import pickle

from logger import Logger


class Score:
    def __init__(self, metrics: Dict[str, float]):
        self.metrics = metrics


class CompetitionScores:
    """Scores archived in the completions. This is a set of 2D arrays for different aspect of evaluation:
    accuracy, clarity, depth of explanation and reasoning"""

    def __init__(self, n_models: int, metric_keys: List[str]):
        self.n_models = n_models
        self.metric_keys = metric_keys
        self.metrics = {key:np.zeros((n_models, n_models), dtype=np.float32) for key in metric_keys}
        self.count = np.zeros((n_models, n_models), dtype=np.int32)

    def update(self, master_model_index: int, student_model_index: int, score: Dict[str, float]):
        for key, value in score.items():
            self.metrics[key][master_model_index][student_model_index] += value
        self.count[master_model_index][student_model_index] += 1

    def dump(self, file_name):
        with open(file_name, 'wb') as file:
            pickle.dump(self, file, protocol=pickle.HIGHEST_PROTOCOL)

    def get_all_avg_results(self):
        count = self.count.copy()
        count[count == 0.0] = 1.0
        avg_score = { key: value/count for key, value in self.metrics.items() }
        return avg_score

    def get_student_avg_score(self):
        return self.__get_avg_score(axis=0)

    def get_master_avg_score(self):
        return self.__get_avg_score(axis=1)

    def __get_avg_score(self, axis):
        count = self.count.sum(axis=axis)
        count[count == 0.0] = 1.0
        # mean of every metric type for each model
        avg_metrics_by_type_and_model = { key:value.sum(axis=axis)/count for key, value in self.metrics.items() }
        avg_score = []
        for model in range(self.n_models):
            avg_scores_for_model = {key:value[model] for key, value in avg_metrics_by_type_and_model.items()}
            avg_score.append(avg_scores_for_model)
        return avg_score


def clean_json_result(json_like):
    i1 = json_like.find('{')
    if i1 < 0:
        raise Exception('Cannot find json')
    i2 = json_like.find('}', i1+1)
    if i2 < 0:
        raise Exception('Cannot find json')
    return json_like[i1:i2 + 1]


def parse_score(raw_json):
    raw_json = clean_json_result(raw_json)
    try:
        return json.loads(raw_json)
    except BaseException:
        Logger.logger.error('Wrong json score:' + raw_json)
    return None
