from typing import Optional
from pydantic import BaseModel

import numpy as np

from logger import Logger


class Score(BaseModel):
    accuracy: Optional[float] = 0.0
    clarity: Optional[float] = 0.0
    depth: Optional[float] = 0.0
    reasoning: Optional[float] = 0.0

    def __init__(self, accuracy=0.0, clarity=0.0, depth=0.0, reasoning=0.0):
        super().__init__()
        self.accuracy = accuracy
        self.clarity = clarity
        self.depth = depth
        self.reasoning = reasoning


class CompetitionScores:
    """Scores archived in the completions. This is a set of 2D arrays for different aspect of evaluation:
    accuracy, clarity, depth of explanation and reasoning"""

    def __init__(self, dim: int):
        self.dim = dim
        self.accuracy = np.zeros((dim, dim), dtype=np.float32)
        self.clarity = np.zeros((dim, dim), dtype=np.float32)
        self.depth = np.zeros((dim, dim), dtype=np.float32)
        self.reasoning = np.zeros((dim, dim), dtype=np.float32)
        self.count = np.zeros((dim, dim), dtype=np.int32)

    def update(self, master_model_index: int, student_model_index: int, score: Score):
        self.accuracy[master_model_index][student_model_index] += score.accuracy
        self.clarity[master_model_index][student_model_index] += score.clarity
        self.depth[master_model_index][student_model_index] += score.depth
        self.reasoning[master_model_index][student_model_index] += score.reasoning
        self.count[master_model_index][student_model_index] += 1

    def get_all_avg_results(self):
        count = self.count.copy()
        count[count == 0.0] = 1.0
        return {'accuracy': self.accuracy / count, 'clarity': self.clarity / count,
                'depth': self.depth / count, 'reasoning': self.reasoning / count}

    def get_student_avg_score(self):
        return self.__get_avg_score(axis=0)

    def get_master_avg_score(self):
        return self.__get_avg_score(axis=1)

    def __get_avg_score(self, axis):
        count = self.count.sum(axis=axis)
        avg_accuracy = self.accuracy.sum(axis=axis) / count
        avg_clarity = self.clarity.sum(axis=axis) / count
        avg_depth = self.depth.sum(axis=axis) / count
        avg_reasoning = self.reasoning.sum(axis=axis) / count
        avg_scores = []
        for n in range(self.dim):
            avg_scores.append(Score(accuracy=avg_accuracy[n], clarity=avg_clarity[n], depth=avg_depth[n],
                                    reasoning=avg_reasoning[n]))
        return avg_scores


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
        return Score.parse_raw(raw_json)
    except BaseException:
        Logger.logger.error('Wrong json response:' + raw_json)
    return None
