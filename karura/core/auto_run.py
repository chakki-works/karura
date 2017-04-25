from collections import OrderedDict
import numpy as np
import pandas as pd
from karura.core.dataframe_extension import DataFrameExtension
from karura.core.insight import InsightIndex
from karura.core.analysis_stop_exception import AnalysisStopException


class AutoRun():

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
            InsightIndex.FEATURE_SELECTION,
            InsightIndex.MODEL_SELECTION
        ]

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

