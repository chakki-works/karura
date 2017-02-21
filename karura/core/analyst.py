from collections import OrderedDict
from karura.core.dataframe_extension import DataFrameExtension
from karura.core.insight import InsightIndex


class Analyst():

    def __init__(self, df, insights):
        self.dfe = DataFrameExtension(df)
        self.insights = insights
        self._check_list = OrderedDict()
        self._check_target = [
            InsightIndex.COLUMN_CHECK_TAG,
            InsightIndex.ROW_CHECK_TAG,
            InsightIndex.PREPROCESSING,
            InsightIndex.FEATURE_AUGMENTATION,
            InsightIndex.FEATURE_SELECTION,
            InsightIndex.MODEL_SELECTION
        ]
        self._insight = None
        self._init_check_list()
        self._descriptions = []
    
    def _init_check_list(self):
        for c in self._check_target:
            self._check_list[c] = False
    
    def is_done(self):
        done = True
        for c in self._check_target:
            if not self._check_list[c]:
                done = False
        return done

    def describe_insight(self):
        if self.has_insight():
            return self._insight.describe()
        else:
            return ""
    
    def analyze(self):
        # fetch remained insights
        insights = []
        for c in self._check_target:
            insights = InsightIndex.query(self.insights, is_done=False, tag=c)
            if len(insights) > 0:
                break
            else:
                self._check_list[c] = True
        
        if self.is_done():
            return True
        else:
            if len(insights) > 0:
                self._proceed(insights)
            return False

    def has_insight(self):
        if self._insight is not None:
            return True
        else:
            return False
    
    def get_descriptions(self):
        return self._descriptions

    def _proceed(self, insights):
        self._descriptions = []
        for i in insights:
            if i.is_applicable(self.dfe):
                if i.automatic:
                    d = i.describe()
                    if d:
                        self._descriptions.append(d)
                    i.adopt(self.dfe)
                    i.index.done = True
                else:
                    self._insight = i
                    break

    def resolve(self, adopt=True):
        if self._insight is not None:
            if adopt:
                self._insight.adopt(self.dfe)
                d = self._insight.describe()
                if d:
                    self._descriptions.append(d)

            self._insight.index.done = True
            self._insight = None
