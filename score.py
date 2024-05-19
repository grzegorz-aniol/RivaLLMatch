from typing import Optional

from pydantic import BaseModel

import numpy as np


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

    def get_results(self):
        return {'accuracy': self.accuracy, 'clarity': self.clarity, 'depth': self.depth, 'reasoning': self.reasoning}

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

    @staticmethod
    def __mean_excluding_diagonal(arr, axis=0) -> np.array:
        if axis not in [0, 1]:
            raise ValueError("Axis must be 0 (columns) or 1 (rows)")

        # Create a mask to exclude diagonal elements
        mask = np.eye(arr.shape[0], dtype=bool)

        if axis == 0:
            # For column-wise mean
            means = []
            for i in range(arr.shape[1]):
                col_without_diag = arr[:, i][~mask[:, i]]
                means.append(np.mean(col_without_diag))
            return np.array(means)
        else:
            # For row-wise mean
            means = []
            for i in range(arr.shape[0]):
                row_without_diag = arr[i, :][~mask[i, :]]
                means.append(np.mean(row_without_diag))
            return np.array(means)


def parse_score(raw_json):
    return Score.parse_raw(raw_json)
