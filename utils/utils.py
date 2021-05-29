import os
import git
from pathlib import Path
from bokeh.models.tools import HoverTool, ResetTool, BoxZoomTool
from bokeh.models import DatetimeTickFormatter, NumeralTickFormatter
from bokeh.plotting import figure


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