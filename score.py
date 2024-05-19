from typing import Optional

from pydantic import BaseModel

import numpy as np


class Score(BaseModel):
    accuracy: Optional[float] = 0.0
    clarity: Optional[float] = 0.0
    depth: Optional[float] = 0.0
    reasoning: Optional[float] = 0.0
    count: Optional[int] = 0

    def __init__(self, accuracy=0.0, clarity=0.0, depth=0.0, reasoning=0.0, count=0):
        super().__init__()
        self.accuracy = accuracy
        self.clarity = clarity
        self.depth = depth
        self.reasoning = reasoning
        self.count = count

    def update_with(self, other_score):
        self.accuracy += other_score.accuracy
        self.clarity += other_score.clarity
        self.depth += other_score.depth
        self.reasoning += other_score.reasoning
        self.count += 1

    def get_avg_score(self):
        if self.count == 0:
            return None
        return Score(accuracy=self.accuracy / self.count, clarity=self.clarity / self.count,
                     depth=self.depth / self.count,
                     reasoning=self.reasoning / self.count)


class CompetitionScores:
    """Scores archived in the completions. This is a set of 2D arrays for different aspect of evaluation:
    accuracy, clarity, depth of explanation and reasoning"""

    def __init__(self, dim: int):
        self.dim = dim
        self.accuracy = np.zeros((dim, dim), dtype=np.float16)
        self.clarity = np.zeros((dim, dim), dtype=np.float16)
        self.depth = np.zeros((dim, dim), dtype=np.float16)
        self.reasoning = np.zeros((dim, dim), dtype=np.float16)
        self.count = np.zeros((dim, dim), dtype=np.int32)

    def update(self, master_model_index: int, student_model_index: int, score: Score):
        self.accuracy[master_model_index][student_model_index] += score.accuracy
        self.clarity[master_model_index][student_model_index] += score.clarity
        self.depth[master_model_index][student_model_index] += score.depth
        self.reasoning[master_model_index][student_model_index] += score.reasoning
        self.count[master_model_index][student_model_index] += 1

    def get_student_avg_score(self):
        return self.__get_avg_score(axis=0)

    def get_master_avg_score(self):
        return self.__get_avg_score(axis=1)

    def __get_avg_score(self, axis):
        avg_accuracy = self.accuracy.mean(axis=axis)
        avg_clarity = self.clarity.mean(axis=axis)
        avg_depth = self.depth.mean(axis=axis)
        avg_reasoning = self.reasoning.mean(axis=axis)
        count = self.count.sum(axis=axis)
        avg_scores = []
        for n in range(self.dim):
            avg_scores.append(Score(accuracy=avg_accuracy[n], clarity=avg_clarity[n], depth=avg_depth[n],
                                    reasoning=avg_reasoning[n], count=count[n]))
        return avg_scores


def parse_score(raw_json):
    return Score.parse_raw(raw_json)
