import os
import re
import pandas as pd
if not os.path.exists("./clenadata"):
    os.makedirs(".clenadata")


class Cleaner:
    def __init__(self):
        self.FolderContent = os.listdir()
