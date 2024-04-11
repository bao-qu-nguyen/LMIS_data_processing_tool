import pandas as pd


class Data():
    def __init__(self):
        self.__df = None
        self.__column_name = []
        self.__column_stat = {}

    def get_data(self):
        return self.__df

    def import_data(self, file_path):
        '''

        :param file_path: path to the data
        :return:
        '''
        self.__df = pd.read_csv(file_path)

    def data_na(self, mode, index_reset):
        '''

        :param mode: Default: drop, Options: drop or average
        :param index_reset: Default: True, Options:  True or False
        :return:
        '''
        self.__df.dropna(inplace=True)

    def data_sort(self, sort_column):
        self.__df.sort_values(by=sort_column, ignore_index=True, inplace=True)

    def data_clean(self, column_names, process):
        """
        :param column_names: list of column(s) of interest
        remove all na from all columns
        :param process: filament, crystal, or adjust

        :return:
        """
        if process == 'filament':
            self.__df.drop(columns=[col for col in self.__df if col not in column_names], inplace=True)
            self.__df = self.__df[
                (self.__df["Unnamed: 0"].astype(str).str.isdigit()) & (self.__df['Lot Number'].notna()) &
                (self.__df['Name'].notna())]
            self.__df = self.__df[(self.__df["Lot Number"].astype(str).str.isdigit()) &
                                  (self.__df["Name"].astype(str).str.isdigit())]
            self.__df = self.__df.dropna()
        if process == 'crystal':
            self.__df.drop(columns=[col for col in self.__df if col not in column_names], inplace=True)
            self.__df = self.__df[
                (self.__df["Unnamed: 0"].astype(str).str.isdigit()) & (self.__df["Lot Number"].notna()) &
                (self.__df['Name'].notna()) & (self.__df["Serial Counter"].astype(str).str.isdigit())]
            self.__df = self.__df[self.__df["Name"].astype(str).str.isdigit()]
            self.__df = self.__df.dropna()
            self.__df['RO_side'] = self.__df[['3:[1]RO_R_side', '3:[2]RO_L_side']].max(axis=1)
            self.__df['RO_f'] = self.__df[['4:[4]RO_r_f', '4:[5]RO_l_f']].max(axis=1)
            self.__df['zone_f'] = self.__df[['4:[9]rt_zone_f', '4:[8]lt_zone_f']].max(axis=1)
            self.__df['end_f'] = self.__df[['4:[11]rt_end_f', '4:[12]lt_end_f']].max(axis=1)
            crystal_columns_mod = ['Unnamed: 0', 'Measurement time', 'Serial Counter', 'Name',
                                   '4:[2]tip_f', 'RO_side', 'RO_f', 'zone_f', 'end_f'
                                   ]
            self.__df.drop(columns=[col for col in self.__df if col not in crystal_columns_mod], inplace=True)
        if process == 'adjust':
            self.__df.drop(columns=[col for col in self.__df if col not in column_names], inplace=True)
            self.__df = self.__df[
                (self.__df["Unnamed: 0"].astype(str).str.isdigit()) & (self.__df['Lot Number'].notna()) &
                (self.__df['Name'].notna())]
            self.__df = self.__df[(self.__df["Lot Number"].astype(str).str.isdigit()) &
                                  (self.__df["Name"].astype(str).str.isdigit())]
            self.__df = self.__df.dropna()

        if process == 'LMIS':
            pass
