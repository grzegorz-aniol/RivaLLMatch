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
        master_scores = self.scores.get_master_avg_score()
        n_models = len(self.model_names)
        n_metrics = len(metric_keys)
        student_overall_scores = np.zeros((n_metrics, n_models))
        master_overall_scores = np.zeros((n_metrics, n_models))
        for i, key in enumerate(metric_keys):
            scores = [score[key] for score in student_scores]
            student_overall_scores[i] = scores
            master_overall_scores[i] = [score[key] for score in master_scores]
            self.generate_overall_results(f'{self.competition_id} / {key}', key,
                                          f'workdir/{self.competition_id}_{key}.png', scores)
            self.generate_heatmap_chart(f'{self.competition_id} / {key} (heatmap)',
                                        f'workdir/{self.competition_id}_{key}_heatmap.png', all_results[key])
        student_average_scores = student_overall_scores.mean(axis=0)
        self.generate_overall_results(f'{self.competition_id} / average student result (received)', 'average',
                                      f'workdir/{self.competition_id}_average_student.png', student_average_scores)

        teacher_average_scores = master_overall_scores.mean(axis=0)
        self.generate_overall_results(f'{self.competition_id} / average master score (given)', 'average',
                                      f'workdir/{self.competition_id}_average_master.png', teacher_average_scores)

        x = np.array([all_results[k] for k in all_results])
        total_heatmap = np.mean(x, axis=0)
        self.generate_heatmap_chart(f'{self.competition_id} / overall heatmap',
                                    f'workdir/{self.competition_id}_average_heatmap.png', total_heatmap)

    def generate_heatmap_chart(self, title, file_name, matrix):
        plt.figure(figsize=(self.fig_width, 6))
        heatmap = sns.heatmap(matrix, annot=True, cmap="YlGnBu",
                              xticklabels=self.model_names, yticklabels=self.model_names)
        heatmap.set_title(title, fontdict=self.title_style)
        heatmap.set_xlabel('students', fontdict=self.axis_style, labelpad=20)
        heatmap.set_ylabel('masters', fontdict=self.axis_style)
        plt.xticks(rotation=-45)
        plt.subplots_adjust(left=0.2, bottom=0.2)

        plt.tight_layout()
        plt.savefig(file_name)
        plt.close()

    def generate_overall_results(self, title, metric_name, file_name, values):
        plt.figure(figsize=(self.fig_width, 6))
        bar_plot = sns.barplot(x=self.model_names, y=values, hue=self.model_names, legend=False,
                               palette=sns.color_palette(n_colors=len(self.model_names)))
        bar_plot.set_title(title, fontdict=self.title_style)
        bar_plot.set_xlabel('Models', fontdict=self.axis_style, labelpad=20)
        bar_plot.set_ylabel(metric_name, fontdict=self.axis_style)
        for index, value in enumerate(values):
            bar_plot.text(index, value + 0.01, f'{value:.3f}', color='black', ha="center")
        plt.subplots_adjust(left=0.2, bottom=0.2)
        y_min = 0.5 if min(values) > 0.5 else 0.0
        bar_plot.set_ylim(bottom=y_min)

        plt.tight_layout()
        plt.savefig(file_name)
        plt.close()
