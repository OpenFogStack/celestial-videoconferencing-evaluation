import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.axes
from matplotlib.colors import ListedColormap

current_palette = sns.color_palette()
cmap = ListedColormap(sns.color_palette(current_palette).as_hex())

sns.set(rc={'figure.figsize':(20,4)}, style='whitegrid', font='CMU Serif')

def save_fig(ax: matplotlib.axes, folder: str, suffix: str, format: str="pdf") -> None:
    fig = ax.get_figure()
    fig.tight_layout()

    fig.savefig(folder + suffix + "." + format)
    fig.clear()

# create an empty dataframe
df_paper = pd.DataFrame()

# go through our experiments
for experiment in ["server", "satellite"]:
    for run in ["1", "2", "3"]:

        # find out how long the total experiment is
        # total is the last start time to the first end time

        actual_start = 0
        actual_end = np.inf
        for client in ["1", "2", "3"]:
            # get the dataframe
            path = os.path.join("..", "results", experiment, run, client + ".csv" )

            df = pd.read_csv(path)
            actual_start = max(df["send_time"].max(), actual_start)
            actual_end = max(df["send_time"].min(), actual_start)

        actual_length = actual_end - actual_start

        required_length = 10 * 60 * 1e9
        cutoff = (actual_length - required_length) / 2

        expected_path = os.path.join("..", "results", experiment, run, "tracker.csv" )

        expected_df = pd.read_csv(expected_path)

        min_t = 0
        if experiment == "server":
            min_t = expected_df[expected_df["path1dist"] > 23.0]["t"].min()
        elif experiment == "satellite":
            min_t = expected_df[expected_df["path2dist"] > 2.0]["t"].min()

        expected_df["t"] = expected_df["t"] - min_t

        # cut off some stuff

        expected_df = expected_df[(cutoff < expected_df["t"]) & (expected_df["t"] < actual_length - cutoff)]

        for client in ["1", "2", "3"]:
            # relevant file is in ../results/[experiment]/[run]/[client].csv
            path = os.path.join("..", "results", experiment, run, client + ".csv" )

            df = pd.read_csv(path)
            other_clients = df["id"].unique()
            df["send_time"] = df["send_time"] - min_t
            df["recv_time"] = df["recv_time"] - min_t

            # cut off some stuff

            df = df[(cutoff < df["send_time"]) & (df["send_time"] < actual_length - cutoff)]
            #df = df[df["latency"] < 500]

            min_t_now = df["send_time"].min()
            df["send_time"] = df["send_time"] - min_t_now
            df["recv_time"] = df["recv_time"] - min_t_now



            for other in other_clients:

                df_run = df[(df["id"] == other)][["latency", "send_time", "packet_len"]]
                # transform index into column and add other columns needed for the figure
                df_run.reset_index(inplace=True, drop=True)
                df_run.insert(0, "Experiment", experiment)
                df_run.insert(1, "Path", str(other) + "-" + client)
                df_run.insert(2, "Run", run)

                df_run["t"] = pd.to_datetime(df_run["send_time"])
                df_run.sort_values(by=["t"], inplace=True)
                df_run["latency_r"] = df_run.rolling('1s', min_periods=1, on="t").median()["latency"]
                df_run["latency_r_log10"] = np.log10(df_run["latency_r"])

                # set column names
                df_run.columns = ["Experiment", "Path", "Run", "Latency", "Time", "packet_len", "t", "Latency_Rolling", "Latency_Rolling_log10"]
                # calculate distribution
                #df_run.sort_values(by="t", ascending=True, inplace=True)
                # add to result df
                df_paper = df_paper.append(df_run)

#df_paper.sort_values(by=["Experiment", "t"], inplace=True)
df_paper.reset_index(inplace=True, drop=True) # optionally reset index

df_paper["Time"] = df_paper["Time"]/1e9
df_paper


ax_paper = sns.lineplot(x="Time", y="Latency_Rolling", data=df_paper[(df_paper["Experiment"] == "server") & (df_paper["Path"] == "3-1")], hue="Run", palette=sns.color_palette("Dark2", n_colors=3), hue_order=["1", "2", "3"], ci=None)
ax_paper.set_xlabel("t [s]")
ax_paper.set_ylabel("Latency (1s Rolling Mean) [s]")
save_fig(ax_paper, "./paper/", "reproducibility-" + "server" + "-" + "3-2", format="pdf")

for experiment in ["satellite", "server"]:
        for path in ["1-2", "1-3", "2-3", "2-1", "3-1", "3-2"]:

            ax_paper = sns.lineplot(x="Time", y="Latency_Rolling", data=df_paper[(df_paper["Experiment"] == experiment) & (df_paper["Path"] == path)], hue="Run", palette=sns.color_palette("Dark2", n_colors=3), hue_order=["1", "2", "3"], ci=None)
            ax_paper.set_xlabel("t [s]")
            ax_paper.set_ylabel("Latency (1s Rolling Mean) [s]")
            save_fig(ax_paper, "./website/reproducibility/", "reproducibility-" + experiment + "-" + path, format="png")

            ax_paper = sns.lineplot(x="Time", y="Latency_Rolling_log10", data=df_paper[(df_paper["Experiment"] == experiment) & (df_paper["Path"] == path)], hue="Run", palette=sns.color_palette("Dark2", n_colors=3), hue_order=["1", "2", "3"], ci=None)
            ax_paper.set_xlabel("t [s]")
            ax_paper.set_ylabel("log10 Latency (1s Rolling Mean)")
            save_fig(ax_paper, "./website/reproducibility/", "reproducibility-log10-" + experiment + "-" + path, format="png")