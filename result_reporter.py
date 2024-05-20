import matplotlib
import numpy as np
matplotlib.use('Agg')
import seaborn as sns
import matplotlib.pyplot as plt

from score import CompetitionScores


class ChartReporter:
    def __init__(self, competition_id: str, model_names: list, scores: CompetitionScores):
        self.competition_id = competition_id
        self.model_names = model_names
        self.scores = scores
        self.title_style = {'fontsize': 16, 'fontweight': 'bold'}
        self.axis_style = {'fontsize': 14, 'fontstyle': 'italic'}
        self.fig_width = max(7, 2 * len(model_names))

    def generate_reports(self):
        all_results = self.scores.get_all_avg_results()
        metric_keys = all_results.keys()
        student_scores = self.scores.get_student_avg_score()
        n_models = len(self.model_names)
        n_metrics = len(metric_keys)
        overall_scores = np.zeros((n_metrics, n_models))
        for i, key in enumerate(metric_keys):
            scores = [score[key] for score in student_scores]
            overall_scores[i] = scores
            self.generate_overall_results(f'{self.competition_id} / {key}', key,
                                          f'results/{self.competition_id}_{key}.png', scores)
            self.generate_heatmap_chart(f'{self.competition_id} / {key} (heatmap)',
                                        f'results/{self.competition_id}_{key}_heatmap.png', all_results[key])
        average_scores = overall_scores.mean(axis=0)
        self.generate_overall_results(f'{self.competition_id} / average result', 'average',
                                      f'results/{self.competition_id}_average.png', average_scores)

    def generate_heatmap_chart(self, title, file_name, matrix):
        plt.figure(figsize=(self.fig_width, 6))
        heatmap = sns.heatmap(matrix, annot=True, cmap="YlGnBu",
                              xticklabels=self.model_names, yticklabels=self.model_names)
        heatmap.set_title(title, fontdict=self.title_style)
        heatmap.set_xlabel('students', fontdict=self.axis_style)
        heatmap.set_ylabel('masters', fontdict=self.axis_style)
        plt.subplots_adjust(left=0.2, bottom=0.2)
        plt.savefig(file_name)
        plt.close()

    def generate_overall_results(self, title, metric_name, file_name, values):
        plt.figure(figsize=(self.fig_width, 6))
        bar_plot = sns.barplot(x=self.model_names, y=values, hue=self.model_names, legend=False,
                               palette=sns.color_palette(n_colors=len(self.model_names)))
        bar_plot.set_title(title, fontdict=self.title_style)
        bar_plot.set_xlabel('Models', fontdict=self.axis_style)
        bar_plot.set_ylabel(metric_name, fontdict=self.axis_style)
        for index, value in enumerate(values):
            bar_plot.text(index, value + 0.01, f'{value:.3f}', color='black', ha="center")
        plt.subplots_adjust(left=0.2, bottom=0.2)
        bar_plot.set_ylim(bottom=min(0.5, min(values)))

        plt.savefig(file_name)
        plt.close()
