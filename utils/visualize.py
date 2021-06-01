from bokeh.models.tools import HoverTool, ResetTool, BoxZoomTool, PanTool
from bokeh.models import DatetimeTickFormatter, NumeralTickFormatter, FuncTickFormatter, BoxAnnotation
from bokeh.plotting import figure
from bokeh.io import show, output_notebook
import networkx as nx
import matplotlib.pyplot as plt
plt.style.use('seaborn')

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


def generae_fig_to_plot_std(df, year, width=330, height=300, hover_tools=HOVER_TOOLS, axis=AXIS, ticks=3):
    fig = figure(
        width=width,
        height=height,
        x_range=list(df.index),
        tools=[ResetTool(), BoxZoomTool(), PanTool()],
        x_axis_label="Month",
        y_axis_label="Total Events" if year == "y_2019" else None,
        title="Follower Events vs STD and Mean",
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

    # creates lines # for the legend legend_label=f"{year.split('_')[1]} mean",
    fig.line(x=df.index, y=df[year], line_width=2, color="#756bb1")
    y = len(df.index) * [df[year].mean()]
    fig.line(x=df.index, y=y, line_width=2, color="#31a354", line_dash="dotted")
    return fig


def plot_network_graph(graph, plot_groups=None):
    pos = nx.spring_layout(graph)
    f, ax = plt.subplots(figsize=(15, 10))
    nodes = nx.draw_networkx_nodes(graph, pos, alpha=0.8)
    if plot_groups is not None:
        nodes = nx.draw_networkx_nodes(graph, pos, cmap=plt.cm.Set1, node_color=plot_groups['group'], alpha=0.8)
        nodes.set_edgecolor('k')
    nx.draw_networkx_labels(graph, pos, font_size=12)
    nx.draw_networkx_edges(graph, pos)