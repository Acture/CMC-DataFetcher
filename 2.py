import pandas as pd

df1 = pd.read_excel("所内币价.xlsx")
df2 = pd.read_excel("CMC_data.xlsx")
df3 = pd.merge(df1,df2,how = 'outer', on=['code'])
print(df3)
df3.to_excel("test.xlsx")