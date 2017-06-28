from collections import OrderedDict
import numpy as np
import pandas as pd
from karura.core.dataframe_extension import DataFrameExtension
from karura.core.insight import InsightIndex
from karura.core.analysis_stop_exception import AnalysisStopException
from karura.core.predictor import PredictorConvertible


class Analyst(PredictorConvertible):

    def __init__(self, df_or_dfe, insights):
        super().__init__(df_or_dfe, insights)
        self._check_list = OrderedDict()
        self._halt = False
        self._insight = None
        self._need_confirmation = False
        self.init()
    
    def init(self):
        self._halt = False
        for c in self._tag_order:
            self._check_list[c] = False
    
    def has_done(self):
        done = True
        if self._halt:
            return done

        for c in self._tag_order:
            if not self._check_list[c]:
                done = False
        return done
    
    def describe(self):
        if self._insight is not None:
            return self._insight.describe()
        else:
            return ""

    def result(self):
        m_insights = InsightIndex.query(self.insights, is_done=True, tag=InsightIndex.MODEL_SELECTION)
        if len(m_insights) == 0 or m_insights[0].model is None:
            return None
        else:
            return m_insights[0]

    def step(self):
        # fetch remained insights
        insights = []
        for c in self._tag_order:
            insights = InsightIndex.query(self.insights, is_done=False, tag=c)
            if len(insights) > 0:
                break
            else:
                self._check_list[c] = True
        
        if self.has_done() or len(insights) == 0:
            return None
        else:
            self._insight = insights[0]
            return self.__step()

    def have_to_ask(self):
        return self._need_confirmation
    
    def __step(self, reply=None):
        i = self._insight
        d = None
        try:
            i.init_description()
            if reply is not None and self._need_confirmation:
                interpreted = i.interpret(reply)
                i.index.done = i.adopt(self.dfe, interpreted)
                self._need_confirmation = False
            elif i.is_applicable(self.dfe):
                if i.automatic:
                    i.index.done = i.adopt(self.dfe)
                    d = i.describe()
                else:
                    d = i.describe()
                    if d:
                        self._need_confirmation = True
            else:
                 d = i.describe()
                 i.index.done = True
    
        except AnalysisStopException as ex:
            self._halt = True
            d = ex.insight.describe()
        
        return d

    def get_reply(self, reply):
        self.__step(reply)
