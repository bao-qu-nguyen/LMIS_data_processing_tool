# Dash app initialization
from dash import Dash, html, dcc, dash_table
# User management initialization
import os
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date, datetime
from dash.dependencies import Input, Output, State


# e. Rule 1: Any single data points that test outside the spec. limits, control limits, or 𝑋 ± 3𝜎 (Zone A).
# f. Rule 2: 2 out of 3 consecutive data points test in or above 𝑋 ± 3𝜎 (Zone A).
# g. Rule 3: 4 out of 5 consecutive data points test in or beyond 𝑋 ± 2𝜎 (Zone B)
# Logic is still off for 1:[1]fil_height_s
# Looking forward only, if found x then skip i by x and append x amount
class SPC:
    def __init__(self):
        self.__df = None
        self.__column_name = []
        self.__column_stat = {}

    def load_df(self, df):
        self.__df = df

    def return_df(self):
        return self.__df

    def convert_numeric(self, column_name):
        self.__df[column_name] = pd.to_numeric(self.__df[column_name])

    def get_column_stat(self, column_name):
        average_value = self.__df[column_name].mean()
        std_value = self.__df[column_name].std()
        zone_3 = [average_value + 3 * std_value, average_value - 3 * std_value]
        zone_2 = [average_value + 2 * std_value, average_value - 2 * std_value]
        zone_1 = [average_value + std_value, average_value - std_value]

        self.__column_stat = {
            "mean": average_value,
            "std": std_value,
            "zone_1_upper": zone_1[0],
            "zone_1_lower": zone_1[1],
            "zone_2_upper": zone_2[0],
            "zone_2_lower": zone_2[1],
            "zone_3_upper": zone_3[0],
            "zone_3_lower": zone_3[1],
        }
        return self.__column_stat

    def get_spc_color(self, column_name, lower_bound, upper_bound):
        self.convert_numeric(column_name)
        num_index = len(self.__df)
        rule_1_color = "red"
        rule_2_color = "orange"
        rule_3_color = "yellow"
        default_color = "green"
        self.get_column_stat(column_name)
        color_list = []
        i = 0
        while i < num_index:
            color_index = 0
            # Rule 1:
            if (self.__df[column_name].iloc[i] < lower_bound) | \
                    (self.__df[column_name].iloc[i] > upper_bound) | \
                    (self.__df[column_name].iloc[i] > self.__column_stat['zone_3_upper']) | \
                    (self.__df[column_name].iloc[i] < self.__column_stat['zone_3_lower']):
                color_list.append(rule_1_color)
                i += 1
            else:
                # Rule 2 :2/3> 2s from the mean
                if i <= (num_index - 3):
                    temp = self.__df[column_name].iloc[i: i + 3]
                    results = (temp > self.__column_stat['zone_2_upper']) | \
                              (temp < self.__column_stat['zone_2_lower'])
                    if len(temp[results]) >= 2:
                        while color_index <= 2:
                            color_list.append(rule_2_color)
                            color_index += 1
                        i += 3
                    else:
                        # Rule 3: 4/5 > 1s from the mean
                        if i <= (num_index - 5):
                            temp = self.__df[column_name].iloc[i: i + 5]
                            results = (temp > self.__column_stat['zone_1_upper']) | \
                                      (temp < self.__column_stat['zone_1_lower'])
                            if len(temp[results]) >= 4:
                                while color_index <= 4:
                                    color_list.append(rule_3_color)
                                    color_index += 1
                                i += 5
                            else:
                                color_list.append(default_color)
                                i += 1
                        else:
                            i += 1
                            color_list.append(default_color)
                else:
                    i += 1
                    color_list.append(default_color)
        df_column_name = f"{column_name}_color"
        self.__df[df_column_name] = color_list
        cond = (self.__df[column_name] < lower_bound) | \
               (self.__df[column_name] > upper_bound) | \
               (self.__df[column_name] > self.__column_stat['zone_3_upper']) | \
               (self.__df[column_name] < self.__column_stat['zone_3_lower'])

        self.__df.loc[cond,df_column_name] = rule_1_color
