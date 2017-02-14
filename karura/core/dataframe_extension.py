import pandas as pd


class DataFrameExtension():
    """
    Manage the Extended information about dataframe columns.
    """

    def __init__(self, df, categoricals=(), numericals=(), datetimes=(), texts=(), uniques=(), target=""):
        self.df = df
        to_list = lambda x: [] if len(x) == 0 else x
        self.categoricals = to_list(categoricals)
        self.numericals = to_list(numericals)
        self.datetimes = to_list(datetimes)
        self.texts = to_list(texts)
        self.uniques = to_list(uniques)
        self.target = to_list(target)

    def to_categorical(self, column_or_columns):
        def convert(c):
            self.df[c].astype("category")
        self.__set_column(column_or_columns, self.categoricals, convert)

    def get_categoricals(self):
        return self.df[[self.categoricals]]

    def to_numerical(self, column_name):
        def convert(c):
            self.df[c] = pd.to_numeric(self.df[c])
        self.__set_column(column_or_columns, self.numericals, convert)

    def get_numericals(self):
        return self.df[[self.numericals]]

    def to_datetime(self, column_name):
        def convert(c):
            self.df[c] = pd.to_datetime(self.df[c])
        self.__set_column(column_or_columns, self.datetimes, convert)

    def get_datetimes(self):
        return self.df[[self.datetimes]]

    def to_text(self, column_name):
        def convert(c):
            self.df[c].astype("str")
        self.__set_column(column_or_columns, self.datetimes, convert)

    def get_texts(self):
        return self.df[[self.texts]]

    def get_uniques(self):
        return self.df[[self.uniques]]

    def get_target(self):
        return self.df[self.target]

    def __set_column(self, column_or_columns, type_column, convert_func):
        column_names = self.__to_list(column_or_columns)
        for c in column_names:
            self.df[c] = convert_func(c)
            if c not in type_column:
                type_column.append(c)

    def __to_list(self, column_or_columns):
        column_names = column_or_columns
        if not isinstance(column_names, (list, tuple)):
            column_names = [column_names]
        return column_names