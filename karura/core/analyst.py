from collections import OrderedDict
from karura.core.dataframe_extension import DataFrameExtension
from karura.core.insight import InsightIndex
from karura.core.analysis_stop_exception import AnalysisStopException


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
        self._halt = False
        self._insight = None
        self._descriptions = []
        self.init()
    
    def init(self):
        self._halt = False
        self._descriptions = []
        for c in self._check_target:
            self._check_list[c] = False
    
    def is_done(self):
        done = True
        if self._halt:
            return done

        for c in self._check_target:
            if not self._check_list[c]:
                done = False
        return done
    
    def get_model_insight(self):
        m_insights = InsightIndex.query(self.insights, is_done=True, tag=InsightIndex.MODEL_SELECTION)
        if len(m_insights) > 0:
            return m_insights[0]
        else:
            return None

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
                try:
                    self._proceed(insights)
                except AnalysisStopException as ex:
                    self._halt = True
                    if ex.insight.describe():
                        self._descriptions = [ex.insight.describe()]
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
                    if i.describe():
                        self._descriptions.append(i.describe())
                    i.index.done = i.adopt(self.dfe)
                else:
                    self._insight = i
                    break
            else:
                if i.describe():
                    self._descriptions.append(i.describe())
                i.index.done = True

    def resolve(self, reply):
        if self._insight is not None:
            interpreted = self._insight.interpret(reply)
            done = self._insight.adopt(self.dfe, interpreted)
            d = self._insight.describe()
            if d:
                self._descriptions.append(d)
            if done:
                self._insight.index.done = True
                self._insight = None
