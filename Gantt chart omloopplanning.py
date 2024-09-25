import pandas as pd
import matplotlib as plt


df1 = pd.read_excel('omloopplanning.xlsx', engine='openpyxl')

print(df1.head())