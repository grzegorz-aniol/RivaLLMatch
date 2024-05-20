import matplotlib
matplotlib.use('Agg')

import seaborn as sns
import matplotlib.pyplot as plt

from score import CompetitionScores


class ChartReporter:
    def __init__(self, competition_id: str, model_names: list, scores: CompetitionScores):
        self.competition_id = competition_id
        self.model_names = model_names
        self.scores = scores
        self.title_style =  {'fontsize': 16, 'fontweight': 'bold'}
        self.axis_style = {'fontsize': 14, 'fontstyle': 'italic'}
        self.fig_width = 3 * len(model_names)

    def generate_reports(self):
        results = self.scores.get_results()
        metric_keys = results.keys()
        student_scores = self.scores.get_student_avg_score()
        for key in metric_keys:
            scores = [score.__getattribute__(key) for score in student_scores]
            self.generate_overall_results(f'{self.competition_id} / {key}', key,
                                          f'results/{self.competition_id}_{key}.png', scores)
            self.generate_heatmap_chart(f'{self.competition_id} / {key} heatmap',
                                        f'results/{self.competition_id}_{key}_heatmap.png', results[key])

    def generate_heatmap_chart(self, title, file_name, matrix):
        plt.figure(figsize=(self.fig_width, 6))
        heatmap = sns.heatmap(matrix, annot=True, cmap="YlGnBu",
                              xticklabels=self.model_names, yticklabels=self.model_names)
        heatmap.set_title(title, fontdict=self.title_style)
        heatmap.set_xlabel('students', fontdict=self.axis_style)
        heatmap.set_ylabel('masters', fontdict=self.axis_style)
        plt.savefig(file_name)
        plt.close()

    def generate_overall_results(self, title, metric_name, file_name, values):
        plt.figure(figsize=(self.fig_width, 6))
        bar_plot = sns.barplot(x=self.model_names, y=values, hue=values, legend=False,
                               palette=sns.color_palette(n_colors=len(self.model_names)))
        bar_plot.set_title(title, fontdict=self.title_style)
        bar_plot.set_xlabel('Models', fontdict=self.axis_style)
        bar_plot.set_ylabel(metric_name, fontdict=self.axis_style)
        for index, value in enumerate(values):
            bar_plot.text(index, value + 0.01, f'{value:.3f}', color='black', ha="center")
        plt.savefig(file_name)
        plt.close()