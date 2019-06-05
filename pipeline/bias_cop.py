import numpy as np
from aequitas.preprocessing import preprocess_input_df
from aequitas.group import Group
from aequitas.plotting import Plot
import ipdb

class BiasCop:
    """
    Wraps Aequitas. Returns metrics measuring bias and fairness of our models.

    Generates "fairness" groups based on the majority demographic in a
    neighborhood.

    Expects to be given a "results_df" that has a label column, a (binary)
    score column, and demographic columns. These demographic columsn should be
    the percentage of people in a block group that belong to the demographic.
    """
    DEFAULT_CONFIG = {
        'label_col': 'label',
        'score_col': 'score',
        'demographics': {
            'af_am_alone': 'num_af_am_alone_percent',
            'hisp': 'num_hisp_percent'
        }
    }

    def __init__(self, results_df, **kwargs):
        self.config = BiasCop.DEFAULT_CONFIG.copy()
        self.config.update(kwargs)
        self.results_df = self._preprocess(results_df)
        self.xtab = None


    def xtabs(self):
        """
        Returns a dataframe with lots of different metrics for each feature
        in the original input dataframe.
        """
        # Cache it
        if self.xtab is not None:
            return self.xtab

        self.xtab, _ = Group().get_crosstabs(self.results_df)
        return self.xtab


    def plot_group_metric(self, metric):
        """
        Returns a plot. You may have to call plt.show() using matplotlib in
        order to see anything.
        """
        xtab = self.xtabs()
        plot = Plot().plot_group_metric(xtab, metric)
        return plot


    def _preprocess(self, df):
        df = self._create_groups(df)

        score_col = self.config['score_col']
        label_col = self.config['label_col']

        # Rename columns to use Aequitas' names
        if label_col != 'label_value':
            df = df.assign(label_value=df[label_col])
            df = df.drop(columns=[label_col])

        if score_col != 'score':
            df = df.assign(score=df[score_col])
            df = df.drop(columns=[score_col])

        # Make sure group col is a string
        df.majority_demo = df.majority_demo.astype(str)

        # Filter to only what Aequitas needs
        columns = ['label_value', 'score', 'majority_demo']
        df, _ = preprocess_input_df(df[columns])

        return df


    def _create_groups(self, df):
        groups = df.apply(lambda row: self._majority(row), axis=1)
        return df.assign(majority_demo=groups.values)


    def _majority(self, df_row):
        for demo, metric in self.config['demographics'].items():
            demo_perc = self._filter_nan(df_row[metric])
            if demo_perc > 0.5:
                return demo

        return 'other'


    def _filter_nan(self, val, fallback=0):
        if val == np.nan:
            return fallback
        elif np.isinf(val):
            return fallback
        else:
            return val or fallback
