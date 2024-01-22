from typing import List


class DrawObjectDesc:
    @property
    def layer(self):
        return 0

    def get_name(self) -> str:
        raise NotImplementedError('Method not implemented')

    def get_properties(self) -> List[str]:
        raise NotImplementedError('Method not implemented')

    def get_hover_properties(self) -> List[str]:
        raise NotImplementedError('Method not implemented')

    def draw(self, df, p):
        raise NotImplementedError('Method not implemented')


class PointDesc(DrawObjectDesc):
    def __init__(self, radius=0.5, draw_units='data', alpha=0.7, legend_label=None):
        self.name = "point"
        self.properties_data = {'latitude': True, 'longitude': True, 'color': False}
        self.radius = radius
        self.draw_units = draw_units  # 'data' or 'screen'
        self.alpha = alpha
        self.legend_label = "" if legend_label is None else legend_label

    def get_name(self) -> str:
        return self.name

    def get_properties(self) -> List[str]:
        return self.properties_data.keys()

    def get_hover_properties(self) -> List[str]:
        return [p for p, v in self.properties_data.items() if v == True]

    def draw(self, df, p):
        self.circles = p.circle(name=self.name, legend_label=self.legend_label, x='longitude', y='latitude',
                                color='color',
                                radius=self.radius if "point_radius" not in df.columns else "point_radius",
                                radius_units=self.draw_units,
                                alpha=self.alpha if "point_alpha" not in df.columns else "point_alpha",
                                source=df)
        return self.circles


class CrossDesc(DrawObjectDesc):
    def __init__(self, size=20, line_width=5, alpha=0.7, legend_label=None):
        self.name = "point"
        self.properties_data = {'latitude': True, 'longitude': True, 'color': False}
        self.size = size
        self.line_width = line_width
        self.alpha = alpha
        self.legend_label = "" if legend_label is None else legend_label

    def get_name(self) -> str:
        return self.name

    def get_properties(self) -> List[str]:
        return self.properties_data.keys()

    def get_hover_properties(self) -> List[str]:
        return [p for p,v in self.properties_data.items() if v==True]

    def draw(self, df, p):
        self.crosses = p.cross(name=self.name, legend_label=self.legend_label, x='longitude', y='latitude',
                               color='color', size=self.size, line_width=self.line_width, alpha=self.alpha, source=df)
        return self.crosses



class TriangleDesc(DrawObjectDesc):
    def __init__(self, radius = 15, alpha=1, legend_label = None):
        self.name = "triangle"
        self.properties_data = { 'latitude': False, 'longitude': False, 'color': False, "facing":False }
        self.radius=radius
        self.alpha = alpha
        self.legend_label = "" if legend_label is None else legend_label

    def get_name(self) -> str:
        return self.name

    def get_properties(self) -> List[str]:
        return self.properties_data.keys()

    def get_hover_properties(self) -> List[str]:
        return [p for p,v in self.properties_data.items() if v==True]


    def draw(self, df, p):
        self.triangles = p.inverted_triangle(name=self.name, legend_label=self.legend_label, x='longitude', y='latitude', angle="facing", fill_color='color', size=self.radius,  alpha=self.alpha, source=df)
        return self.triangles


class ConnectedLineDesc(DrawObjectDesc):
    def __init__(self, width = 1, alpha=1, legend_label = None):
        self.name = "connected_line"
        self.properties_data = { 'lat': False, 'lon': False, 'color': False }
        self.width=width
        self.alpha=alpha
        self.legend_label = "" if legend_label is None else legend_label

    @property
    def layer(self):
        return -8

    def get_name(self) -> str:
        return self.name

    def get_properties(self) -> List[str]:
        return self.properties_data.keys()

    def get_hover_properties(self) -> List[str]:
        return [p for p,v in self.properties_data.items() if v==True]

    def draw(self, df, p):
        renderers = []
        for _, row in df.iterrows():
            r = p.line(row["lon"], row["lat"], name=self.name,  legend_label=self.legend_label, color=row["color"], line_width = self.width, alpha = self.alpha)
            renderers.append(r)
        return renderers


class LineDesc(DrawObjectDesc):
    def __init__(self, width = 1, line_dash='solid', alpha=0.5, legend_label = None):
        self.name = "line"
        self.properties_data = { 's_lat': False, 's_lon': False, 'e_lat': False, 'e_lon': False, 'color': False }
        self.width=width
        self.line_dash=line_dash
        self.alpha=alpha
        self.legend_label = "" if legend_label is None else legend_label

    @property
    def layer(self):
        return -10

    def get_name(self) -> str:
        return self.name

    def get_properties(self) -> List[str]:
        return self.properties_data.keys()

    def get_hover_properties(self) -> List[str]:
        return [p for p,v in self.properties_data.items() if v==True]

    def draw(self, df, p):

        if "ys" not in df.columns or "xs" not in df.columns:
            df["xs"] = df.apply(lambda r: [r["s_lon"], r["e_lon"]]  ,axis=1)
            df["ys"] = df.apply(lambda r: [r["s_lat"], r["e_lat"]]  ,axis=1)

        line_dash = "line_dash" if "line_dash" in df.columns else self.line_dash
        line_width = "line_width" if "line_width" in df.columns else self.width
        return p.multi_line(xs='xs', ys='ys',color='color',
                line_width=line_width, line_dash=line_dash, name=self.name, legend_label=self.legend_label,
                source=df)
                


class WedgeDesc(PointDesc):
    def __init__(self, radius=0.5, draw_units = 'data', legend_label = None):
        super().__init__(radius=radius, draw_units = draw_units, legend_label=legend_label)
        self.name = "wedge"
        self.properties_data.update({'facing': True})

    def draw(self, df, p):

        if "facing_error" not in df.columns:
            wedge_width = 1
            df['start_angle'] = 360 - ((360 + (df['facing'] - wedge_width) - 90) % 360)
            df['end_angle']   = 360 - ((360 + (df['facing'] + wedge_width) - 90) % 360)
        else:
            df['start_angle'] = 360 - ((360 + (df['facing'] - df['facing_error']/2) - 90) % 360)
            df['end_angle']   = 360 - ((360 + (df['facing'] + df['facing_error']/2) - 90) % 360)            

        return p.wedge(name=self.name, x='longitude', y='latitude', legend_label=self.legend_label,
                fill_color='color', radius=self.radius*2,
                start_angle='start_angle', end_angle='end_angle',
                radius_units = self.draw_units,
                start_angle_units='deg',
                end_angle_units='deg',
                direction='clock',
                source = df)

class ElipseDesc(PointDesc):
    def __init__(self, draw_units = 'data', legend_label = None):
        super().__init__(radius=0, draw_units=draw_units)
        self.name = "ellipse"
        self.properties_data.update({ 'ellipse_angle': False,
                                    'size_x': False, 'size_y': False,})
        self.legend_label = "" if legend_label is None else legend_label

    def draw(self, df, p):
        fill_color = "ellipse_color" if "ellipse_color" in df.columns else "color"

        return p.ellipse(name=self.name, legend_label=self.legend_label, x='longitude', y='latitude', width='size_x', width_units=self.draw_units, height='size_y', height_units=self.draw_units, \
                    angle = 'ellipse_angle', fill_color=fill_color, fill_alpha=0.25, line_color="black", source=df)

class Pose2DDrawDesc(WedgeDesc):
    def __init__(self, radius=0.5, draw_units = 'data', legend_label = None):
        super().__init__()
        self.name = "transform_draw"

        self.pointdesc = PointDesc(radius=radius, draw_units=draw_units, legend_label=legend_label)
        self.wedgedesc = WedgeDesc(radius=radius, draw_units=draw_units, legend_label=legend_label)
        self._update_names()

    def _update_names(self):
        self.pointdesc.name = self.name 
        self.wedgedesc.name = self.name

    def _draw_from_df(self, df, p):
        a = self.pointdesc.draw(df, p)
        b = self.wedgedesc.draw(df, p)
        return a,b

    def draw(self, df, p):
        result = self._draw_from_df(df, p)
        return result

class UncertainPose2DDrawDesc(Pose2DDrawDesc):
    def __init__(self, radius=0.5, draw_units = 'data', legend_label = None):
        self.ellipsedesc = None
        super().__init__(radius=radius, draw_units=draw_units, legend_label=legend_label)
        self.name = "uncertain_"+ self.name
        self.ellipsedesc = ElipseDesc(draw_units=self.draw_units, legend_label=legend_label)
        self._update_names()
        self.properties_data.update(self.ellipsedesc.properties_data)
        self.properties_data.update({ 'facing_error': False})

    def _update_names(self):
        self.pointdesc.name = self.name
        self.wedgedesc.name = self.name
        if self.ellipsedesc:
            self.ellipsedesc.name = self.name 

    def draw(self, df, p):
        # draw ellipse        
        result = [self.ellipsedesc.draw(df,p)]
        result.extend(self._draw_from_df(df,p))
        return result
