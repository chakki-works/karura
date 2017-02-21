# -*- coding: utf-8 -*-
from karura.core.insight import Insight


class TargetConfirmInsight(Insight):

    def __init__(self):
        super().__init__()
        self.index.as_column_check()

    def is_applicable(self, dfe):
        if dfe.target:
            return False
        else:
            return True
    
    def adopt(self, dfe, interpreted=None):
        if not interpreted:
            return 0
