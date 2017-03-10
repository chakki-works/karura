import re
from enum import Enum
from collections import OrderedDict
import numpy as np
import pandas as pd


class FType(Enum):
    categorical = 0
    numerical = 1
    datetime = 2
    text = 3
    unique = 4


class DataFrameExtension():
    """
    Manage the Extended information about dataframe columns.
    """

    def __init__(self, df, categoricals=(), numericals=(), datetimes=(), texts=(), uniques=(), target=""):
        to_list = lambda x: [] if len(x) == 0 else x
        self.df = df
        self.target = target
        self.ftypes = OrderedDict()
        self._ftype_inference()

        for columns, dtype in zip(
            [categoricals, numericals, datetimes, texts, uniques],
            [FType.categorical, FType.numerical, FType.datetime, FType.text, FType.unique]
        ):
            for c in columns:
                self.ftypes[c] = dtype
            if dtype == FType.categorical:
                self.to_categorical(columns)
            elif dtype == FType.numerical:
                self.to_numerical(columns)
            elif dtype == FType.datetime:
                self.to_datetime(columns)
    
    def _ftype_inference(self):
        dtypes = self.df.dtypes
        border = (5, 2)
        for c in dtypes.index:
            sample = self.df[c].head(border[0])
            if dtypes[c] in (np.int32, np.int64, np.float32, np.float64):
                self.ftypes[c] = FType.numerical
            elif sample.apply(lambda x: re.match(r"\d{2,4}?/\d{1,2}?/\d{1,2}?", str(x)) is not None).sum() > border[1]:
                self.ftypes[c] = FType.datetime
                self.to_datetime(c)
            else:
                self.ftypes[c] = FType.text
    
    def get_target_ftype(self):
        if self.target and self.target in self.ftypes:
            return self.ftypes[self.target]
        else:
            return None

    def load_column_definition(self, path):
        # todo: implements
        pass

    def save_column_definition(self, path):
        # todo: implements
        pass

    def to_categorical(self, column_or_columns):
        def convert(c):
            self.df[c] = self.df[c].astype("category")
        self.__convert_column(column_or_columns, FType.categorical, convert)
    
    def to_numerical(self, column_or_columns):
        def convert(c):
            self.df[c] = pd.to_numeric(self.df[c])
        self.__convert_column(column_or_columns, FType.numerical, convert)

    def to_datetime(self, column_or_columns):
        def convert(c):
            self.df[c] = pd.to_datetime(self.df[c])
        self.__convert_column(column_or_columns, FType.datetime, convert)

    def to_text(self, column_or_columns):
        def convert(c):
            self.df[c] = self.df[c].astype("str")
        self.__convert_column(column_or_columns, FType.text, convert)
    
    def to_unique(self, column_or_columns):
        self.__convert_column(column_or_columns, FType.unique, None)
    
    def sync(self):
        new_ftype = OrderedDict()
        for c in self.df.columns:
            if c in self.ftypes:
                new_ftype[c] = self.ftypes[c]
        self.ftypes = new_ftype

    def get_features(self, ftype=None):
        if ftype is None:
            features = [c for c in self.df.dtypes.index if c != self.target]
        else:
            features = []
            for c in self.ftypes:
                if self.ftypes[c] == ftype and c != self.target:
                    features.append(c)
        
        if len(features) > 0:
            return self.df[features]
        else:
            return None

    def get_columns(self, ftype=None, include_target=True):
        features = self.get_features(ftype)
        columns = []
        if features is not None:
            columns = features.columns.tolist()
        if include_target and (ftype is None or self.target and self.ftypes[self.target] == ftype):
            columns += [self.target]
        return columns

    def get_target(self):
        if self.target:
            return self.df[self.target]
        else:
            raise Exception("target column is not defined.")

    @classmethod
    def read_csv(cls, path, **kwargs):
        df = pd.read_csv(path, **kwargs)
        return cls(df)

    def __convert_column(self, column_or_columns, ftype, convert_func):
        column_names = self.__to_list(column_or_columns)
        for c in column_names:
            if convert_func:
                convert_func(c)
            self.ftypes[c] = ftype

    def __to_list(self, column_or_columns):
        column_names = column_or_columns
        if not isinstance(column_names, (list, tuple)):
            column_names = [column_names]
        return column_names