import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os, sys, glob, copy

from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.embed import components
from bokeh.models import HoverTool, ResetTool, WheelZoomTool, PanTool, BoxZoomTool, ResizeTool

import re, cStringIO, uuid


def HWInfoCVSCleanup(fileIn, fileOut=None):
    length = None
    if (fileOut is None):
        output = cStringIO.StringIO()
    else:
        output = open(fileOut, 'w')

    with open(fileIn, 'r') as fin:
        for line in fin:
            if (length is None): # first line
                value = re.split('\",\"', line.strip())
                value = value[0].split(',') + value[1:]
                value = [x.replace('"',"") for x in value]
                value = [x.replace(",", " ") for x in value]
                length= len(value)
            else:
                value = line.strip().split(',')

            if (length is None):
                length = len(value)

            output.write(','.join(value[:length])+"\n")
            if (len(value) != length):
                pass
    if (fileOut is not None):
        output.close()
        output = fileOut
    return output


class Resource(object):

    class Config(object):
        def __init__(self, data={}):
            self.pointStep = 1
            self.pointSize = 3

            if ('pointStep' in data.keys()): self.pointStep = data['pointStep']
            if ('pointSize' in data.keys()): self.pointSize = data['pointSize']


    def __init__(self, logfile=None, realtime=False):
        self.df = None
        if (logfile is not None):
            print("Load the log file %s." %logfile)
            self.df = Resource._loadHWInfoFromLogFile(logfile)


    def getInfo(self):
        start = self.df.index.values[0].astype('M8[ms]').astype('O')
        end   = self.df.index.values[-1].astype('M8[ms]').astype('O')
        feilds= self.df.columns.values
        return (start, end, feilds)

    def toDB(self, dbid, folder= "db", type='pickle'):
        """
        save the data to the database
        """
        #import pickle
        if (not os.path.exists(folder)):
            os.makedirs(folder)
        if (type=='pickle'):
            self.df.to_pickle( os.path.join(folder, Resource.dbName(dbid, type)) )
        else:
            print('support pickle type only.')
        pass

    @staticmethod
    def fromDb(dbname, type='pickle'):
        ret =  Resource()
        if (type != 'pickle'):
            print('support pickle type only.')
            raise ValueError('Support pickle type only.')
        ret.df = pd.read_pickle(dbname)
        return ret

    @staticmethod
    def dbName(dbid, type='pickle'):
        ret = None
        if (type == 'pickle'):
            ret = '{0}.{1}'.format(dbid, type)
        return ret

    @staticmethod
    def _loadHWInfoFromLogFile(log_HWiINFO64):

        if (isinstance(log_HWiINFO64, list)):
            fileList  = log_HWiINFO64
        else:
            fileList  = [log_HWiINFO64]

        dfs = []
        for item in fileList:
            try:
                df_HWINFO = pd.read_csv(item, encoding='latin_1')
            except:
                pass
                fileOut = '~'+ uuid.uuid1().get_hex() + '.txt'
                fileOut = HWInfoCVSCleanup(fileIn, fileOut)
                df_HWINFO = pd.read_csv(fileOut, encoding='latin_1')
                os.remove(fileOut)

            # uniform the datetime
            ts = pd.to_datetime(df_HWINFO.Date + " " + df_HWINFO.Time, format='%d.%m.%Y %H:%M:%S.%f')
            df_HWINFO.drop(['Date', 'Time'], axis=1, inplace=True)
            df_HWINFO['DateTime'] = ts
            df_HWINFO.set_index('DateTime', inplace=True)
            df_HWINFO = df_HWINFO.convert_objects(convert_numeric='force')
            dfs.append(df_HWINFO)

        df = pd.concat(dfs)
        df = df.drop_duplicates()
        return df


    def generatePlot(self, start=None, end=None, fields = None, others=None, config={}):

        config = Resource.Config(config)
        # get the data from the defined time span
        if (start is None or end is None):
            t_df = self.df
        else:
            idx = (self.df.index >= start) & (self.df.index <= end)
            t_df = self.df[idx]

        if fields is None:
            fields = u'Virtual Memory Commited [MB]'
        if (fields not in self.getInfo()[-1]):
            print('%s is not available ' % fields)
            fields = u'Virtual Memory Commited [MB]'

        # data points for the hover tool
        source = ColumnDataSource(
            data=dict(
            x=t_df.index.values[::config.pointStep],
            y=t_df[fields].values[::config.pointStep],
            desc=[pd.to_datetime(x).strftime('%Y-%m-%d %H:%M:%S.%f') for x in t_df.index.values[::config.pointStep]]
            )
           )
        hover = HoverTool(
                tooltips=[
                    ("index", "$index"),
                    ("(x,y)", "($x, $y)"),
                    ('value', "@y"),
                    ("desc",  "@desc")
                ]
            )
        TOOL = [hover, ResetTool(), BoxZoomTool(), WheelZoomTool(),
                PanTool(), ResizeTool()]

        # figure
        p = figure(title="", plot_width=1300, plot_height=400,
                   x_axis_type="datetime",
                   tools = TOOL, webgl = True)
                   #tools = "hover,pan,wheel_zoom,box_zoom,reset,resize")
        p.line(x=t_df.index.values,
               y=t_df[fields].values, legend=fields)
        p.circle_x(x=t_df.index.values[::config.pointStep],
                   y=t_df[fields].values[::config.pointStep],
                   size=config.pointSize,
                   color="#DD1C77", fill_alpha=0.2)

        # draw hover points
        p.circle('x', 'y', size=config.pointSize, source=source)

        # generate the content
        script, div = components(p)
        print('[{0}]'.format(script[:50]))
        script = re.sub(r'<script type="text/javascript">', '', script)
        script = re.sub(r'\n</script>$','', script)
        print('return js, and div.')
        return (script, div)



if __name__ == "__main__":
    print('--')
