import pandas as pd
from bokeh.models import HoverTool, WheelZoomTool, MultiChoice, Select
from bokeh.plotting import figure, show
from bokeh.layouts import row, column
from bokeh.tile_providers import CARTODBPOSITRON, get_provider, OSM
from bokeh.models.callbacks import CustomJS
from bokeh.io import curdoc
from bokeh import events
from bokeh.plotting import output_notebook

from collections import defaultdict
from typing import List
from draw_drescriptos import *


def on_event(base_viz):
    """
    Function that returns a Python callback to pretty print the events.
    """
    def python_callback(event):
        cls_name = event.__class__.__name__

        for listener, args in base_viz.event_listeners[cls_name]:
            listener(base_viz, event, *args)

    return python_callback

def on_drop_down_event(base_viz, callback_func, args):
    """
    Function that returns a Python callback to pretty print the events.
    """
    def python_callback(attr, old, new):
        callback_func(base_viz, new, *args)

    return python_callback




class BaseVisualiser:
    def __init__(self, relative_frame=False, osm_provider = False, inside_notebook=True):
        self.object_descriptors = dict()
        self.event_listeners = defaultdict(list)
        self.dropdown_widgets = list()
        self.object_values = defaultdict(list)
        self.relative_frame = relative_frame
        self.map_provider = OSM if osm_provider else CARTODBPOSITRON
        self.inside_notebook=inside_notebook
        self.__construct_figure()

        # add default descriptors, custom descritors can be added afterwards
        self.add_object_desc(PointDesc())
        self.add_object_desc(TriangleDesc())
        self.add_object_desc(LineDesc())
        self.add_object_desc(ConnectedLineDesc())
        self.add_object_desc(WedgeDesc())
        self.add_object_desc(ElipseDesc())
        self.add_object_desc(TranformDrawDesc())
        self.add_object_desc(MeasuredTranformDrawDesc())

    def __construct_figure(self):
        if self.inside_notebook:
            output_notebook()
            
        # range bounds supplied in web mercator coordinates
        if self.relative_frame:
            p = figure(width=1000, height=1000,
                        tools="tap,wheel_zoom,pan,reset",
                        match_aspect=True)
        else:
            p = figure(x_axis_type="mercator", y_axis_type="mercator",
                tools="tap,wheel_zoom,pan,reset",
                width=1000, height=1000)
            tile_provider = get_provider(self.map_provider)
            p.add_tile(tile_provider)

        p.toolbar.active_scroll = p.select_one(WheelZoomTool)
        self.figure = p

    def add_object_desc(self, object_desc : DrawObjectDesc):
        self.object_descriptors[object_desc.get_name()] = object_desc

    def add_event_listener(self, event_name, callback_func, args=None):
        self.event_listeners[event_name].append((callback_func, args))

    def add_entry_object(self, name, entry_value_dict):
        # check if entry is valid
        for property in self.object_descriptors[name].get_properties():
            if property not in entry_value_dict:
                assert False, f"{property} missing from entry for {name}!" 
        self.object_values[name].append(entry_value_dict)

    def add_entries_dataframe(self, name, objects_dataframe):
        objects_dataframe.loc[objects_dataframe.astype(str).drop_duplicates().index]
        objects_entries = objects_dataframe.to_dict(orient="records")
        df_columns = list(objects_dataframe.columns)

        for property in self.object_descriptors[name].get_properties():
            assert property in df_columns, f"{property} missing from entry for {name}!" 
            assert not objects_dataframe[property].isnull().values.any(),  f"{property} data has null values in {name}!" 

        self.object_values[name].extend(objects_entries)

    def add_dropdown_option(self, menu, callback_func, args=None):
        if type(menu)==list:
            values, options = menu, menu  
        elif type(dict):
            values =  [item for item, v in menu.items() if v]
            options = list(menu.keys())
        else:
            assert False, "invalid arg type !"

        dropdown = MultiChoice(value=values, options=options)
        self.dropdown_widgets.append((dropdown, callback_func, args))


    def add_select_option(self, select_list, selected_idx, callback_func,title_txt="", args=None):
        select_obj = Select(value=select_list[selected_idx], title=title_txt, options=select_list)
        self.dropdown_widgets.append((select_obj, callback_func, args))

    def clear_scene(self):
        self.figure.tools = self.figure.tools[:4]
        self.figure.renderers = [] if self.relative_frame else [self.figure.renderers[0]]
        self.object_values = defaultdict(list)


    def render(self):
        self.draw_objects()
        self.figure.legend.location = "top_left"
        self.figure.legend.click_policy="hide"
        return self.figure 

    def draw_objects(self):
        # display scene objects
        object_descriptors = sorted(self.object_descriptors.values(), key=lambda x: x.layer, reverse=False)
        self.renderers = dict()
        for object_desc in object_descriptors:
            name=object_desc.get_name()
            if name in self.object_values and len(object_desc.get_hover_properties())>0:
                column_tuple_list = [ (c, f"@{c}") for c in object_desc.get_hover_properties()]
                if len(column_tuple_list)>0:
                    self.figure.add_tools(
                        HoverTool(
                        names=[name],
                        tooltips=column_tuple_list,
                        )
                    )
            df = pd.DataFrame.from_dict(self.object_values[name])
            if len(df)>0:
                start_idx = len(self.figure.renderers) 
                indices = [start_idx]
                renderers = object_desc.draw(df, self.figure)
                if(type(renderers)==tuple or type(renderers)==list):
                    indices = list(range(start_idx, start_idx+len(renderers)))
                self.renderers[name] = indices   

    def plot(self):
        # show figure
        p = self.figure
        if self.inside_notebook:
            self.render_handle = show(p, notebook_handle=True)
        else:
            drop_downs_widgets = []
            for drop_down_info in self.dropdown_widgets:
                dropdown, callback_func, args = drop_down_info
                drop_downs_widgets.append(dropdown)
                dropdown.on_change('value', on_drop_down_event(self, callback_func, args))
            p.on_event(events.Tap, on_event(self))
            if len(drop_downs_widgets)>0:
                layout = row(
                    column(*drop_downs_widgets),
                    p,
                )      
            else:
                layout=p      
            self.render_handle = curdoc().add_root(layout)

    def display(self):
        self.render()
        self.plot()
