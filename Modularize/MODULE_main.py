from MODULE_historicaldata import historical_data_extraction
from MODULE_dataframe_output import return_dataframe
from MODULE_data_validation import validation
import pandas as pd

history_data_list = historical_data_extraction()
df = return_dataframe(history_data = history_data_list)
validation(df=df)





