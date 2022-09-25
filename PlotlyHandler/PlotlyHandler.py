from plotly.subplots import make_subplots
import plotly.graph_objects as go
from autoscience.imageConverter import *
import numpy as np

class PlotlyHandler:

    def __init__(self):
        print("This is Constructor")
        
    def __del__(self):
        print("This is Destructor")

    @staticmethod
    def makeSubplots(rows=None,cols=None,specs=None):
        fig = make_subplots( rows=rows, cols=cols, specs=specs)
        return fig

    @staticmethod
    def addTrace(fig=None, contents=None, row=None, col=None):
        fig.add_trace(contents, row=row, col=col)

    @staticmethod
    def show(fig=None):
        fig.show()

    @staticmethod
    def updateLayout(fig=None,scene=None):
        fig.update_layout(scene=scene)

    @staticmethod
    def updateTrace(trace=None,showscale=None):
        trace.update(showscale=showscale)

    @staticmethod
    def updateCameraEyePosition(fig=None,x=None,y=None,z=None):
        fig.update_layout(scene_camera_eye=dict(x=x, y=y, z=z))

    @staticmethod
    def writeHtml(fig,fileNameHTML=None):
        fig.write_html(fileNameHTML)

    @staticmethod
    def addScatterPlotData(fig=None,df=None,colNameX=None,colNameY=None,row=None,col=None):
        PlotlyHandler.addTrace( fig, go.Scatter(x= df[colNameX],y= df[colNameY], name=colNameY), row=row, col=col)

    @staticmethod
    def addScatterPlotDataByList(fig=None,df=None,colNameX=None,colNameYList=None,row=None,col=None):
        for i in range(len(colNameYList)):
            colNameY = colNameYList[i]
            PlotlyHandler.addScatterPlotData(fig,df,colNameX,colNameY,row,col)

    @staticmethod
    def addScatterPlotByGivenData(fig=None,xList=None,yList=None,name=None,row=None,col=None,marker=None, mode=None, text=None):
        PlotlyHandler.addTrace( fig, go.Scatter(x= xList,y= yList, name=name, marker=marker, mode=mode, text=text), row=row, col=col)

    @staticmethod
    def Scatter3d(x=None,y=None,z=None,mode=None,marker=None,name=None, hoverinfo=None, line=None, showlegend=True):
        return go.Scatter3d( x=x, y=y, z=z, mode=mode, marker=marker, name=name, line=line, hoverinfo=hoverinfo, showlegend=showlegend )

    @staticmethod
    def Surface(x=None,y=None,z=None,colorscale=None,hoverinfo=None):
        return go.Surface(x=x, y=y, z=z, colorscale=colorscale, hoverinfo=hoverinfo)
    
    @staticmethod
    def Cone(x=None,y=None,z=None,u=None,v=None,w=None,sizeref=None,colorscale=None):
        return go.Cone(x=x, y=y, z=z, u=u, v=v, w=w, sizeref=sizeref, colorscale=colorscale)
    
    @staticmethod
    def drawArraw(fig,p0,p1,sizeref=0.1,color=None,hoverinfo="skip",row=None,col=None,enlargeRatio=1.0):
        p1Loc   = p0 + enlargeRatio*(p1-p0)
        nvec    = p1Loc-p0
        nvecMag = np.sqrt(nvec[0]**2 + nvec[1]**2 + nvec[2]**2)
        nvec    = nvec/nvecMag
        pArrow  = p1Loc

        trace = PlotlyHandler.Cone(x=[pArrow[0]], y=[pArrow[1]], z=[pArrow[2]], u=[nvec[0]], v=[nvec[1]], w=[nvec[2]], sizeref=sizeref*nvecMag, colorscale=[[0, color], [1,color]] )
        PlotlyHandler.updateTrace(trace=trace,showscale=False)
        PlotlyHandler.addTrace( fig=fig, contents=trace, row=row, col=col )

        trace = PlotlyHandler.Scatter3d( x=[p0[0],p1Loc[0]], y=[p0[1],p1Loc[1]], z=[p0[2],p1Loc[2]], mode="lines", marker=dict(color=color), hoverinfo=hoverinfo, name="", showlegend=False)
        PlotlyHandler.addTrace( fig=fig, contents=trace, row=row, col=col )

    @staticmethod
    def addLineSegment(fig=None, x0=None, y0=None, x1=None, y1=None, color=None, name=None, text=None, row=None, col=None):
        PlotlyHandler.addShape(fig=fig, type="line", xref="x", yref="y", x0=x0, y0=y0, x1=x1, y1=y1, line=dict(color=color,width=3), name=name, row=row, col=col ) 
        xm = int((x0+x1)/2)
        ym = int((y0+y1)/2)
        PlotlyHandler.addScatterPlotByGivenData(fig=fig, xList=[xm], yList=[ym], marker=dict(color=color, size=1), mode="markers", name=name, text=text, row=row, col=col )

    @staticmethod
    def addShape( fig=None, type=None, xref=None, yref=None, x0=None, y0=None, x1=None, y1=None, line=None, name=None, row=None, col=None):
        fig.add_shape( type=type, xref=xref, yref=yref, x0=x0, y0=y0, x1=x1, y1=y1, line=line, name=name, row=row, col=col ) 

    @staticmethod
    def drawCoordinateSystem(fig,pOrg,pX,pY,pZ,sizeref=0.1,hoverinfo="skip",row=None,col=None,enlargeRatio=None):
        PlotlyHandler.drawArraw(fig,pOrg,pX,sizeref=sizeref,color="red"  ,hoverinfo=hoverinfo,row=row,col=col,enlargeRatio=enlargeRatio)
        PlotlyHandler.drawArraw(fig,pOrg,pY,sizeref=sizeref,color="green",hoverinfo=hoverinfo,row=row,col=col,enlargeRatio=enlargeRatio)
        PlotlyHandler.drawArraw(fig,pOrg,pZ,sizeref=sizeref,color="blue" ,hoverinfo=hoverinfo,row=row,col=col,enlargeRatio=enlargeRatio)

    @staticmethod
    def makePairPlot(df=None,varNameList=None,varNameForMarkerColor=None,width=None,height=None,title=""):
        labelNameList = [ varNameList[i].capitalize() for i in range(len(varNameList)) ]
        dimensions    = []
        for i in range(len(varNameList)):
            dimensions.append(dict(label=labelNameList[i], values=df[varNameList[i]]))

        textd = ['non-diabetic' if cl==0 else 'diabetic' for cl in df[varNameForMarkerColor]]

        fig = go.FigureWidget(data=go.Splom(
                                dimensions=dimensions,
                                marker=dict(color=df[varNameForMarkerColor],
                                            size=5,
                                            colorscale='Bluered',
                                            line=dict(width=0.5,color='rgb(230,230,230)')),
                                text=textd,
                                diagonal=dict(visible=False)))

        fig.update_layout(title=title, dragmode='select',width=width,height=height,hovermode='closest')
        #fig.show()
        return fig

    @staticmethod
    def makeImagePlot(img,isOpenCVImage=None,displayOnly=None):

        if isOpenCVImage:
            imgLoc = ImageConverter.ImageConvertCv2Pillow(img)
        else:
            imgLoc = img

        import plotly.express as px

        fig = px.imshow(imgLoc)
        fig.update_layout(coloraxis_showscale=False)
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)

        if displayOnly:
            fig.show()
        else:
            return fig
    
    @staticmethod
    def makePropertyPolarPlot(df=None,fillType='none',RadialAxisVisible=False,displayOnly=None):
        valueRange = [df.min().min(),df.max().max()]

        numRow   = df.shape[0]
        numCol   = df.shape[1]
        nameList = list(df.columns)
        nameList.append(nameList[0])

        fig = go.Figure()
        for irow in range(numRow):
            valueList = list(df[irow:irow+1].values[0])
            valueList.append(valueList[0])
            itemName = df.index[irow]

            fig.add_trace(go.Scatterpolar(
                    r=valueList,
                    theta=nameList,
                    fill=fillType,
                    name=itemName
            ))

        fig.update_layout(
            polar=dict(
            radialaxis=dict(
                visible=RadialAxisVisible,
                range=valueRange,
            )),
            showlegend=True
        )

        if displayOnly:
            fig.show()
        else:
            return fig


