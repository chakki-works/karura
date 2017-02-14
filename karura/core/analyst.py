from karura.core.dataframe_extension import DataFrameExtension
from karura.core.insight import InsightIndex


class Analyst():

    def __init__(self, df, insights):
        self.dfe = DataFrameExtension(df)
        self.insights = insights
        self._column_checked = False
        self._row_checked = False
        self._model_checked = False
        self._insight = None
    
    def analyze(self):
        if not self._column_checked:
            self.check_columns()

        if self._column_checked:
            return True
        else:
            return False
    
    def describe_insight(self):
        if self.has_insight():
            return self._insight.describe()
        else:
            return ""

    def check_columns(self):
        insights = InsightIndex.query_column_checks(self.insights)
        if len(insights) == 0 or self._column_checked:
            self.column_checked = True
            return True
        else:
            self._proceed(insights)
            return False

    def has_insight(self):
        if self._insight is not None:
            return True
        else:
            return False

    def _proceed(self, insights):
        for i in insights:
            if i.is_invoked_by(self.dfe):
                if i.automatic:
                    i.apply(self.dfe)
                else:
                    self._insight = i
                    break

    def resolve(self, adopt=True):
        if self._insight is not None:
            if adopt:
                self._insight.adopt(self.dfe)
            self._insight.index.done = True
            self._insight = None
