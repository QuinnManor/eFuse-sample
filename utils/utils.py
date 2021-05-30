import os
import git
from pathlib import Path
from bokeh.models.tools import HoverTool, ResetTool, BoxZoomTool, PanTool
from bokeh.models import DatetimeTickFormatter, NumeralTickFormatter, FuncTickFormatter, BoxAnnotation
from bokeh.plotting import figure
from bokeh.io import show, output_notebook
import pandas as pd


HOVER_TOOLS = {
    "date": [HoverTool(
        tooltips={"Total Events":"@y{0,0}","Date":"$x{%F}"},
        formatters={"$x":"datetime","$y":"printf"}
    ), ResetTool(), BoxZoomTool()],
    "hour": [HoverTool(
        tooltips={"Total Events":"@y{0,0}","Hour":"@x"},
        formatters={"$y":"printf"}
    ), ResetTool(), BoxZoomTool()],
    "year": [HoverTool(
        tooltips={"Total Events":"@y{0,0}","Year":"@x"},
        formatters={"$y":"printf"}
    ), ResetTool(), BoxZoomTool()],
    "month": [HoverTool(
        tooltips={"Total Events":"@y{0,0}","Month":"@x"},
        formatters={"$y":"printf"}
    ), ResetTool(), BoxZoomTool()],
}

AXIS = {
    "date": DatetimeTickFormatter(months="%Y-%m-%d"),
    "hour": NumeralTickFormatter(format="0"),
    "year": NumeralTickFormatter(format="0")
}


def get_path(x):
    repo_root = Path(git.Repo(os.getcwd(), search_parent_directories=True).git.rev_parse("--show-toplevel"))
    return f"{repo_root}/data/{x}"


def generae_fig_to_plot(df, width=330, height=300, hover_tools=HOVER_TOOLS, axis=AXIS, ticks=3):
    x_label = df.columns[0]
    y_label = df.columns[-1]
    fig = figure(
        width=width,
        height=height,
        tools=[ResetTool(), BoxZoomTool()],
        x_axis_label=x_label.title(),
        y_axis_label=y_label.title().replace("_", " ") if x_label == "date" else None,
        title = f"{x_label.title()} vs {y_label.title().replace('_', ' ')}"
    )

    # adding circle to graphs for max
    fig.circle(df.loc[df['total_events'].idxmax()][0], df.loc[df['total_events'].idxmax()][-1], size=10, 
               line_color="green", fill_alpha=0.0)

    # adding circle to graphs for min
    fig.circle(df.loc[df['total_events'].idxmin()][0], df.loc[df['total_events'].idxmin()][-1], size=10,
               line_color="red", fill_alpha=0.0)

    tools = hover_tools[x_label][0]
    fig.add_tools(tools)

    # create line
    fig.line(df.iloc[:, 0], df.iloc[:, -1])

    # fiddle with axis and ticks
    fig.xaxis[0].formatter = axis[x_label]
    fig.yaxis[0].formatter = NumeralTickFormatter(format="0,")
    fig.xaxis[0].ticker.desired_num_ticks = ticks

    # center title
    fig.title.align = 'center'
    return fig


def plot_multi_lines(df, width=330, height=300, hover_tools=HOVER_TOOLS):
    fig = figure(
        width=850,
        x_range=list(df.index),
        tools=[ResetTool(), BoxZoomTool(), PanTool()],
        x_axis_label="Month",
        y_axis_label="Total Events",
        title = "Examining Follower Events over the Months",
    )

    # fiddle with axis and ticks
    fig.yaxis[0].formatter = NumeralTickFormatter(format="0,")

    # center title
    fig.title.align = 'center'

    tools = hover_tools["month"][0]
    fig.add_tools(tools)

    # creates lines
    fig.line(x=list(df.index), y=df['y_2019'], line_width=2, color="#3182bd", legend_label="2019")
    fig.line(x=df.index, y=df['y_2020'], line_width=2, color="#756bb1", legend_label="2020")
    fig.line(x=df.index, y=df['y_2021'], line_width=2, color="#31a354", legend_label="2021")

    show(fig)


def get_monthly_event_count(df):
    df_copy = df.groupby("date", as_index=False).size().copy()
    df_copy["year"] = df_copy["date"].dt.strftime('%Y')
    df_copy["month"] = df_copy["date"].dt.strftime('%b')
    df_copy = df_copy.groupby(["year", "month"], as_index=False).sum().rename(columns={"size":"total_events"})
    return df_copy.set_index("month")


def create_time_series_df(df, sd="2019-01-01", ed="2021-12-31", fill_nans=False):
    date_range = pd.date_range(sd, ed).strftime("%b")
    new_df = pd.DataFrame(index=date_range.unique())
    for year in df.year.unique():
        new_df[f"y_{year}"] = df[df["year"] == year]["total_events"]

    if fill_nans:
        new_df.fillna(method="ffill", inplace=True)
        new_df.fillna(0, inplace=True)
    return new_df


def generae_fig_to_plot_std(df, year, width=330, height=300, hover_tools=HOVER_TOOLS, axis=AXIS, ticks=3):
    fig = figure(
        width=width,
        height=height,
        x_range=list(df.index),
        tools=[ResetTool(), BoxZoomTool(), PanTool()],
        x_axis_label="Month",
        y_axis_label="Total Events",
        title = "Examining Follower Events over the Months",
    )

    # fiddle with axis and ticks
    fig.yaxis[0].formatter = NumeralTickFormatter(format="0,")
    fig.axis.formatter = FuncTickFormatter(code="""
    if (index % 2 == 0)
    {
    return tick;
    }
    else
    {
    return "";
    }
    """)
    
    # center title
    fig.title.align = 'center'

    y_mean = df[year].mean()
    y_std = df[year].std()
    upper_std = y_mean + y_std
    
    low_box = BoxAnnotation(top=y_std, fill_alpha=0.1, fill_color='red')
    mid_box = BoxAnnotation(bottom=y_std, top=upper_std, fill_alpha=0.1, fill_color='green')
    high_box = BoxAnnotation(bottom=upper_std, fill_alpha=0.1, fill_color='red')

    fig.add_layout(low_box)
    fig.add_layout(mid_box)
    fig.add_layout(high_box)
    
    tools = hover_tools["month"][0]
    fig.add_tools(tools)

    # creates lines
    fig.line(x=df.index, y=df[year], line_width=2, color="#756bb1")
    fig.line(x=df.index, y=df[year].mean(), line_width=2, color="#31a354", legend_label=f"{year.split('_')[1]} average", line_dash="dotted")
    return fig