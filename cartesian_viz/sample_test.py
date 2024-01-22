from pyproj import Transformer

from engine import BaseVisualiser 
from draw_descriptors import Pose2DDrawDesc, LineDesc

def merc(latlon):
    return Transformer.from_crs("WGS84","EPSG:3857").transform(*latlon)[::-1]


# custom oject inherited from already available one
#________________________________________________________
class CustomPose2D(Pose2DDrawDesc):
    def __init__(self):
        super().__init__()
        self.name = "Custom"+ Pose2DDrawDesc().get_name()
        self._update_names()
        # adding new properties on already existing description
        self.properties_data.update({'type': True})

# construct object entries from data   
#________________________________________________________
def get_entry_data(latlon, heading, type_str,col="blue"):
    latlon=merc(latlon)
    object_instance = {"latitude":latlon[0], "longitude":latlon[1], "facing":heading, 'type':type_str, "color":col}
    return object_instance

       
def get_line_entry(p1,p2, color="red"):
    p1=merc(p1)
    p2=merc(p2)
    return { 's_lat': p1[0], 's_lon': p1[1], 'e_lat': p2[0], 'e_lon': p2[1], 'color': color }



# events demo
def on_tap_event(base_viz, event, arg):
    print("Tap event !")

def on_toggle_option(base_viz, values, arg):
        # clear and update the frame
        base_viz.clear_scene()
        visualiser_sample(inside_notebook=False, g_initialised=True, 
            show_obj1="obj1" in values,
            show_obj2="obj2" in values,
            show_obj3="obj3" in values,
            )
        


# Visualisation
#________________________________________________________


def visualiser_sample(inside_notebook=False, g_initialised=False, show_obj1=True, show_obj2=True, show_obj3=True):
    # init viz
    if g_initialised is False:
        base_viz = BaseVisualiser(inside_notebook=inside_notebook)

        # register custom draw object description 
        base_viz.add_object_desc(CustomPose2D())


        #register callbacks events
        base_viz.add_event_listener("Tap", on_tap_event, args=[base_viz]) 
        base_viz.add_dropdown_option(["obj1", "obj2", "obj3"] , on_toggle_option, args=[base_viz])
        visualiser_sample.base_viz = base_viz
    else:
        base_viz = visualiser_sample.base_viz

    # draw objects
    if show_obj1:
        obj_1 = get_entry_data([46.7655178,23.6027677],0,"CUSTOM", col="blue")
        base_viz.add_entry_object(CustomPose2D().get_name(), obj_1)

    if show_obj2:
        obj_2 = get_entry_data([46.7655178,23.6027677 + 0.00002],-30,"CUSTOM_LEFT", col="green")
        base_viz.add_entry_object(CustomPose2D().get_name(), obj_2)

    if show_obj3:
        obj_3 = get_entry_data([46.7655178,23.6027677- 0.00002],30,"CUSTOM_RIGHT", col="red")
        base_viz.add_entry_object(CustomPose2D().get_name(), obj_3)
    
    line_entry = get_line_entry([46.7655178,23.6027677], [46.7655178,23.6027677+ 0.00002])
    base_viz.add_entry_object(LineDesc().get_name(), line_entry)

    # display all
    base_viz.render()
    return base_viz




#call
viz = visualiser_sample()
viz.plot()