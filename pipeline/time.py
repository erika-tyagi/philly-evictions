import pandas as pd

def split_by_year(df, colname='year', drop_col=False):
    """
    Returns a list of two-tuples where the first element in the tuple is a
    training set dataframe and the second element is the corresponding test set
    dataframe. There is a test set for each year except the first. The training
    set consists of all years before the test set.

    For example, given a dataframe with data for 2012, 2013, 2014, and 2015
    this function returns dataframes for the years:

    [(2012, 2013), (2012-2013, 2014), (2012-2014, 2015)]
    """
    min_year = df[colname].min()
    test_years = range(min_year + 1, df[colname].max() + 1)
    year_tuples = [(range(min_year, year), year) for year in test_years]
    return [_df_tuple(df, colname, drop_col, year_tuple)
            for year_tuple in year_tuples]


def _df_tuple(df, colname, drop_col, year_tuple):
    train_range, test_year = year_tuple
    train_df = df[df[colname].isin(train_range)]
    test_df = df[df[colname] == test_year]

    if drop_col:
        train_df = train_df.drop(columns=[colname])
        test_df = test_df.drop(columns=[colname])

    return train_df, test_df