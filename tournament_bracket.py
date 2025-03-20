import pandas as pd
import random
import os

class TableGenerator():
    def __init__(self):
        pass

    def generate_table(self, names:list, output_path=""):
        random.shuffle(names)
        col_1_values = [None for _ in range(2)] + ["X"] + names
        table = {"col_1": col_1_values}
        for index, name in enumerate(names):
            none_before_x = [None] * index
            none_after_x = [None] * ((len(names) - len(none_before_x)) - 1)
            x_position = none_before_x + ["X"] + none_after_x
            values = [None for _ in range(2)] + [name] + x_position
            table[f"col_{index+2}"] = values
        table_df = pd.DataFrame(table)
        if not output_path:
            output_path = os.path.join( os.getcwd(), "table.xlsx")
        table_df.to_excel(output_path)


    def calculate_wins(self, scores_df):
        scores_df.rename(columns={scores_df.columns[0]: "Opponent"}, inplace=True)
        df_columns = scores_df.columns
        result_dict = {}
        for column in df_columns[1:]:
            player_scores_df = scores_df[[df_columns[0],  column]]
            player_scores_df = player_scores_df.explode(column)
            player_scores_df = player_scores_df.where(player_scores_df[column] != "X").dropna()
            player_scores_df["Splitted_set"] = player_scores_df[column].str.split(":")
            player_scores_df["Won_Gems"] = player_scores_df["Splitted_set"].apply(lambda x: x[0] if isinstance(x, list) else None)
            player_scores_df["Lost_Gems"] = player_scores_df["Splitted_set"].apply(lambda x: x[1] if isinstance(x, list) else None)
            player_scores_df["Won_Set"] = player_scores_df["Won_Gems"] > player_scores_df["Lost_Gems"]

            cols_to_convert = ["Won_Gems", "Lost_Gems"]
            player_scores_df[cols_to_convert] = player_scores_df[cols_to_convert].apply(pd.to_numeric, errors='coerce')

            summed_scores_df = player_scores_df.groupby([df_columns[0]])[["Won_Gems","Lost_Gems", "Won_Set"]].sum()

            summed_scores_df.rename(columns={"Won_Set": "Won_Sets"}, inplace=True)
            sets_lost = player_scores_df.groupby("Opponent")["Won_Set"]\
                                            .apply(lambda x: (x == False).sum()).rename("Lost_Sets")

            final_scores_df = pd.merge(summed_scores_df, sets_lost, how="left",on=["Opponent"])
            final_scores_df["Won_Match"] = final_scores_df["Won_Sets"] > final_scores_df["Lost_Sets"]
            result_dict[column] = final_scores_df

        return result_dict

    def calculate_total_results(self, result_dict):
        header = ["Name", "Won_Gems", "Lost_Gems", "Won_Sets", "Lost_Sets", "Won_Matches"]
        final_values = []
        for player, player_df in result_dict.items():
            won_gems = player_df["Won_Gems"].sum()
            lost_gems = player_df["Lost_Gems"].sum()
            won_sets = player_df["Won_Sets"].sum()
            lost_sets = player_df["Lost_Sets"].sum()
            won_maches = player_df["Won_Match"].sum()
            final_values.append([player, won_gems,  lost_gems, won_sets,
                                 lost_sets, won_maches])
        df = pd.DataFrame(final_values, columns=header)
        df = df.sort_values(by=["Won_Matches", "Won_Sets", "Won_Gems"], ascending=[False, False, False])
        return df

    def flatten_result_table(self, result_table_path):
        result_df = pd.read_excel(result_table_path, index_col=None).dropna()
        result_df = result_df.drop(result_df.columns[0], axis=1)
        result_df = result_df.replace(",", "", regex=True).astype(str)
        result_df.columns = result_df.iloc[0]
        result_df = result_df[1:].reset_index(drop=True)
        for col in result_df.columns[1:]:
            result_df[col] = result_df[col].str.split(" ")
        return result_df

    def generate_counted_table(self, table_path, output_path=""):
        flattend_df = table_generator.flatten_result_table(table_path)
        result_dict = table_generator.calculate_wins(flattend_df)
        result_df = table_generator.calculate_total_results(result_dict)
        if not output_path:
            output_path = os.path.join( os.getcwd(), "scores.xlsx")
        result_df.to_excel(output_path)


if __name__ == "__main__":
    names = ["Andy Murray", "Rafael Nadal", "Roger Federer", "Carlos Alcaraz", "Gaël Monfils"]
    table_generator = TableGenerator()
    pd_df = table_generator.generate_table(names)
    table_generator.generate_counted_table("/home/rszczygielski/pythonVSC/tournament_bracket_generator/main_test.xlsx")
