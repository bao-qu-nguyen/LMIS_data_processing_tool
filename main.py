from data_prep import Data
from data_spc import SPC
import pandas as pd
import sqlalchemy
import pyodbc
import datetime

output_path = r'\\hlsql01\beamtech\LMIS\LMIS Reports\\'
conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, ' \
           r'*.accdb)};DBQ=\\hlsql01\beamtech\Summit\Summit_Ion_Manufacturing_be - LMIS.mdb;'
conn = pyodbc.connect(conn_str)

df_coil = pd.read_sql('select * from tbl_LMIS_Coil', conn)
df_LMIS = pd.read_sql('select * from tblLMIParent left join tblLMIChild on tblLMIParent.SN = tblLMIChild.LMISN ', conn)

df_coil = df_coil[df_coil['DateTime'].notna() & df_coil['Coil_SN'].notna() & df_coil['Cone_Ht'].notna() &
                  df_coil['Tip_Radius'].notna() & df_coil['Cone_Offset'].notna() & df_coil['Cone_Angle'].notna() &
                  df_coil['Assembler'].notna()
                  ]
df_coil.sort_values(by='DateTime', ignore_index=True, inplace=True)
df_coil.reset_index(inplace=True, drop=True)

df_coil_spc = SPC()
df_coil_spc.load_df(df_coil)
coil_columns = [
    'Cone_Ht', 'Tip_Radius', 'Cone_Offset', 'Cone_Angle'
]
for column in coil_columns:
    # key = list(column.keys())[0]
    lower_bound = -400
    upper_bound = 400
    # lower_bound = list(list(column.values())[0])[0]
    # upper_bound = list(list(column.values())[0])[1]
    df_coil_spc.get_spc_color(column, lower_bound, upper_bound)
df_coil_final = df_coil_spc.return_df()
df_coil_final.to_csv(output_path + 'LMIS_spc_cleaned.csv')

# For now, Remove rows with WW and ignore reistance
# This depends on which process comes first. It's likely that reistance plays a factor in dipping?

df_LMIS = df_LMIS[df_LMIS['WW'].notna() & df_LMIS['DatePass'].notna() & df_LMIS['PassCode'].notna()]
df_LMIS = df_LMIS[df_LMIS['DatePass'] >= datetime.datetime.now() - pd.to_timedelta("365day")]
df_LMIS = df_LMIS[(df_LMIS['Reistance'] > 10) & (df_LMIS['Reistance'] < 100)]
df_LMIS['Reistance'].fillna((df_LMIS['Reistance'].mean()), inplace=True)
df_LMIS['DW'].fillna((df_LMIS['DW'].mean()), inplace=True)
df_LMIS['W_diff'] = (df_LMIS['WW'] - df_LMIS['DW']) / 10.
df_LMIS = df_LMIS[(df_LMIS['W_diff'] > -50) & (df_LMIS['W_diff'] < 50)]

df_LMIS.sort_values(by='DatePass', ignore_index=True, inplace=True)
df_LMIS.reset_index(inplace=True, drop=True)
LMIS_Gallium_columns = [
    'W_diff', 'Reistance'
]
df_LMIS_spc = SPC()
df_LMIS_spc.load_df(df_LMIS)
for column in LMIS_Gallium_columns:
    # key = list(column.keys())[0]
    lower_bound = -400
    upper_bound = 400
    # lower_bound = list(list(column.values())[0])[0]
    # upper_bound = list(list(column.values())[0])[1]
    df_LMIS_spc.get_spc_color(column, lower_bound, upper_bound)
df_LMIS_final = df_LMIS_spc.return_df()
df_LMIS_final.to_csv(output_path + 'LMIS_LMIS_spc_cleaned.csv')
