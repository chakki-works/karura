from enum import Enum
from karura.env import get_lang


class Insight():
    LANG = get_lang()

    def __init__(self):
        self.lang = self.LANG
        self.description = {}
        self.index = InsightIndex()
        self.automatic = False
    
    def describe(self):
        if self.lang in self.description:
            return self.description[self.lang]
        elif len(self.description) > 0:
            return list[self.description.values()][0]
        else:
            return ""
    
    def is_applicable(self, dfe):
        self.description = {}  # initialize
        its = self.get_insight_targets(dfe)
        if len(its) > 0:
            return True
        else:
            return False

    def adopt(self, dfe, interpreted=None):
        raise Exception("You have to implements apply method")
    
    def get_insight_targets(self, dfe):
        return []
    
    def interpret(self, reply):
        if reply:
            return True
        else:
            return False


class InsightIndex():
    COLUMN_CHECK_TAG = "column_check"
    ROW_CHECK_TAG = "row_check"
    PREPROCESSING = "preprocessing"
    FEATURE_AUGMENTATION = "feature_augmentation"
    FEATURE_SELECTION = "feature_selection"
    MODEL_SELECTION = "model_selection"

    def __init__(self, done=False, tags=()):
        self.done = done
        self.tags = [] if len(tags) == 0 else tags
    
    def as_column_check(self):
        self.append_tag(self.COLUMN_CHECK_TAG)
    
    def as_row_check(self):
        self.append_tag(self.ROW_CHECK_TAG)
    
    def as_preprocessing(self):
        self.append_tag(self.PREPROCESSING)
    
    def as_feature_augmentation(self):
        self.append_tag(self.FEATURE_AUGMENTATION)

    def as_feature_selection(self):
        self.append_tag(self.FEATURE_SELECTION)

    def as_model_selection(self):
        self.append_tag(self.MODEL_SELECTION)

    def append_tag(self, tag_name):
        if tag_name not in self.tags:
            self.tags.append(tag_name)

    @classmethod
    def query(cls, insights, is_done=None, tag=""):
        done_criteria = lambda x: True if is_done is None or x.index.done == is_done else False
        tag_criteria = lambda x: True if tag == "" or tag in x.index.tags else False
        items = [i for i in insights if done_criteria(i) and tag_criteria(i)]
        return items
