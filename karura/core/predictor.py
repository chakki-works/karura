import os
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib
from karura.core.insight import InsightIndex
from karura.core.dataframe_extension import DataFrameExtension
from karura.env import get_store_path


class PredictorConvertible():

    def __init__(self, df_or_dfe, insights):
        if isinstance(df_or_dfe, DataFrameExtension):
            self.dfe = df_or_dfe
        else:
            self.dfe = DataFrameExtension(df_or_dfe)
        self.insights = insights
        self._tag_order = [
            InsightIndex.COLUMN_CHECK_TAG,
            InsightIndex.ROW_CHECK_TAG,
            InsightIndex.PREPROCESSING,
            InsightIndex.FEATURE_AUGMENTATION,
            InsightIndex.LABEL_FORMAT,
            InsightIndex.FEATURE_SELECTION,
            InsightIndex.MODEL_SELECTION
        ]
    
    def to_predictor(self):
        return Predictor.create(self.dfe, self.insights, self._tag_order)


class Predictor():

    def __init__(self, pipeline):
        self.pipeline = pipeline
    
    @classmethod
    def create(cls, dfe, insights, tag_order):
        transformers = []
        label_formatter = None
        for t in tag_order:
            t_insights = InsightIndex.query(insights, tag=t)

            if t == InsightIndex.LABEL_FORMAT:
                label_formatter = t_insights[0].get_transformer(dfe)
            elif t == InsightIndex.MODEL_SELECTION:
                model = t_insights[0].get_transformer(dfe)
                p = PredictionEstimator(model, label_formatter)
                transformers.append(("DataFormatter", DataFormatter(dfe)))
                transformers.append((model.__class__.__name__, p))
            else:
                for i in t_insights:
                    tf = i.get_transformer(dfe)
                    if tf is not None:
                        transformers.append((i.__class__.__name__, tf))
        
        pipe = Pipeline(transformers)
        return Predictor(pipe)
    
    def predict(self, X):
        return self.pipeline.predict(X)

    def save(self, path, model_name):
        if not os.path.exists(path):
            os.mkdir(path)
        joblib.dump(self.pipeline, os.path.join(path, "{}.pkl".format(model_name)))
        return path

    @classmethod
    def load(cls, path, model_name):
        if not os.path.exists(path):
            raise Exception("Model file does not exist.")
        pipeline = joblib.load(os.path.join(path, "{}.pkl".format(model_name)))
        return Predictor(pipeline)

    def save_to_env(self, env, app_id):
        path = get_store_path()
        path = os.path.join(path, env.domain)
        return self.save(path, app_id)

    @classmethod
    def load_from_env(cls, env, app_id):
        path = get_store_path()
        path = os.path.join(path, env.domain)
        return cls.load(path, app_id)


class PredictionEstimator(BaseEstimator, TransformerMixin):

    def __init__(self, model, label_formatter):
        self.model = model
        self.label_formatter = label_formatter

    def fit(self, X, y=None):
        return self  # do nothing (already trained)

    def predict(self, X):
        pred = self.model.predict(X)
        pred_f = self.label_formatter.inverse_transform(pred)
        return pred_f


class DataFormatter(BaseEstimator, TransformerMixin):

    def __init__(self, dfe):
        self.model_target = dfe.target
        self.model_features = dfe.get_columns(include_target=False)

    def fit(self, X, y=None):
        return self  # do nothing

    def transform(self, X, y=None, copy=None):
        columns = X.columns.tolist()
        extras = [c for c in columns if c not in self.model_features]
        extras += [self.model_target]
        for e in extras:
            if e in X.columns:
                X.drop(e, inplace=True, axis=1)

        for f in self.model_features:
            if f not in X.columns:
                raise Exception("Feature {} is not supplied.".format(f))

        X = X[self.model_features]  # order by collect feature
        return X
