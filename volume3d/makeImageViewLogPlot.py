import pandas as pd
import numpy as np



import bokeh
import bokeh.plotting
from bokeh.models import HoverTool, ResetTool, PanTool,WheelZoomTool, BoxZoomTool
from bokeh.models import BoxSelectTool
from bokeh.models import FuncTickFormatter
from bokeh.models import FixedTicker, Label
from bokeh.models.sources import ColumnDataSource
from bokeh.resources import CDN
from bokeh.embed import file_html

from jinja2 import Template


def makeImageViewLogPlot(df, outputfile=None, queryInfo=None, show=False):
    """
    This function generates a static page for the ImageView log data.

    df: pandas.DataFrame or csv(filename or buffer)

    """
    if (isinstance(df, pd.DataFrame)):
        pass
        print('input is pandas.DataFrame')
    else:
        print('load from csv')
        df = pd.read_csv(df, parse_dates=['time'])

    qdiv = bokeh.models.widgets.Div(text=""" """)
    qtemplate = """
    <div>Table: {{data.table}}
    </div>
    <div>Query:
    {{data.query}}
    </div>
    """
    if (queryInfo is not None):
        text = Template(qtemplate).render(data=queryInfo)
        qdiv = bokeh.models.widgets.Div(text=text, width=1200, height=200)

    MAX_MESSAGE_LENGTH = 100
    CATEGORY = dict()
    INVERSE_CATEGORY = dict()

    def reverseDict(dict1):
        dict2 = {}
        for key, value in dict1.items():
            dict2[value] = key
        return dict2


    def invertCATEGORY():
        for key, value in CATEGORY.items():
            INVERSE_CATEGORY[value] = key

    def ticker(tick):
        #print(tick)
        if (tick in INVERSE_CATEGORY):
            return INVERSE_CATEGORY[tick]
        else:
            return "UNKNOWN"

    def toColor(x):
        colorMap = {'Error': 'red',
                    'Warn' : 'pink',
                    'Info' : 'green',
                    'Debug': 'blue',
                    'Trace': 'darkgrey',
                   }
        if (x in colorMap):
            return colorMap[x]
        else:
            return 'orange'

    def toTimeStr(x):
        return str(x).split()[-1]

    def trimLetter (x):
        if (x>MAX_MESSAGE_LENGTH):
            return x[:MAX_MESSAGE_LENGTH]
        else:
            return x

    def categorySet(x):
        x = x.split('.')[-1]
        if (x not in CATEGORY):
            CATEGORY[x] = len(CATEGORY)+1
        return CATEGORY[x]

    # reformat the data
    df['mytime'] = df.loc[:,['time']] - df['time'][0] # offset the time(starting from 0)
    df['type'  ] = map(categorySet, df['logger'])
    df['color']  = map(toColor, df['level'])
    df['msg']    = map(trimLetter, df['message'])
    df['timeStr']= map(toTimeStr, df['mytime'])
    invertCATEGORY()
    #print(CATEGORY)
    #print(INVERSE_CATEGORY)
    # make the source data oject and send to bokeh
    source = ColumnDataSource(
        data=dict(
            x      =df['mytime'],
            y      =df['type'],
            timeStr=df['timeStr'],
            logger =df['logger'],
            msg    =df['msg'],
            color  =df['color'],
        )
    )

    hover = HoverTool(
        tooltips=[
            ("index", "$index"),
            ("time",  "@timeStr"),
            ("logger","@logger"),
            ("msg",   "@msg")
        ]
    )
    if (outputfile is not None):
        bokeh.plotting.output_file(outputfile)

    p = bokeh.plotting.figure(x_axis_type = "datetime",
          tools=[PanTool(dimensions=['width']), WheelZoomTool(dimensions=['width']), hover, ResetTool() ],
          plot_width=1600, plot_height=800,
          name="Plot",webgl=False)
    p.ygrid.minor_grid_line_color = None
    ## \TODO ticker thing does not working. IT is a static one at this monment
    ## Hope the future release would fix it
    #p.yaxis.formatter = FuncTickFormatter.from_py_func(ticker)
    p.circle('x', 'y', size=4, color=df['color'], alpha=0.2, source = source)
    """
    Work around to add the label
    for key, value in CATEGORY.items():
        label = Label(x=-20, y=value, x_units='screen', text=key,
                      text_font_size='5pt', text_font_style = 'italic',
                      render_mode='css',
             border_line_color=None, border_line_alpha=0.0,
             background_fill_color='white', background_fill_alpha=1.0)
        #p.add_layout(label)
    """

    output = bokeh.layouts.Column(qdiv, p)

    if (show):
        bokeh.io.show(output)
    else:
        bokeh.io.save(output)



if __name__ == '__main__':

    # only load the click while it is used as command line
    import click
    @click.command()
    @click.option('--show', default=False, help='open HTML on browser.')
    @click.option('--output', default='c:/temp/output.html', help='output HTML file.')
    @click.option('--input', default='C:/Users/10101891/Downloads/Export (11).csv',
                    help='input csv file.',
                    type=click.Path(exists=True))
    #@click.argument('inputCsvFile')
    def run(input, output, show):
        csvfile = input
        makeImageViewLogPlot(pd.read_csv(csvfile, parse_dates=['time']),
                            outputfile=output, show=show)

    # run it
    run()
