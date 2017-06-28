from collections import OrderedDict
import numpy as np
import pandas as pd
from karura.core.dataframe_extension import DataFrameExtension
from karura.core.insight import InsightIndex
from karura.core.analysis_stop_exception import AnalysisStopException
from karura.core.predictor import PredictorConvertible


class AutoRun(PredictorConvertible):

    def __init__(self, df_or_dfe, insights):
        super().__init__(df_or_dfe, insights)

    def result(self):
        m_insights = InsightIndex.query(self.insights, tag=InsightIndex.MODEL_SELECTION)
        if len(m_insights) == 0 or m_insights[0].model is None:
            return None
        else:
            return m_insights[0]

    def execute(self):
        descriptions = []
        for tag in self._tag_order:
            insights = InsightIndex.query(self.insights, tag=tag)
            if len(insights) == 0:
                continue
            
            try:

                for i in insights:
                    if i.is_applicable(self.dfe):
                        if i.automatic:
                            i.adopt(self.dfe)
                        else:
                            # try to execute automatically
                            i.adopt(self.dfe)
                    d = i.describe()
                    if d:
                        descriptions.append(d)

            except AnalysisStopException as ex:
                descriptions.append(ex.insight.describe())
                break
        
        return descriptions

