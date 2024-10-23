import json
import uuid

from bokeh.embed import file_html, json_item
from bokeh.models import (Circle, ColumnDataSource, GraphRenderer, HoverTool,
                          Legend, LegendItem, SaveTool, StaticLayoutProvider)
from bokeh.plotting import figure
from bokeh.resources import CDN
from numpy import arange, array, cos, pi, random, sin
from pandas import DataFrame
from rest_framework import permissions, status, views
from rest_framework.response import Response

from external.models import LearnerRecord


class GraphView(views.APIView):
    """
    Generate Bokeh Graphs
    """
    queryset = LearnerRecord.objects.all()
    # queryset = Configuration.objects.all()
    # filter_backends = [filters.ObjectPermissionsFilter]
    # authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        scale_factor = 40

        users = request.query_params.getlist(
            'users') if 'users' in request.query_params else ("User A", "User B", "User C")
        if len(users) > 10:
            return Response("Maximum 10 users",
                            status=status.HTTP_400_BAD_REQUEST)
        dict_values = {
            'ksats': ['Knowledge of Cybersecurity', 'Ability in fork-bomb attacks', 'Skill in Kali',],
            # 'User A': [60, 90, 30],
            # 'User B': [10, 16, 99],
            # 'User C': [0, 33, 50],
        }
        for u in users:
            dict_values[u] = random.randint(0, 100, 3)

        values = DataFrame(data=dict_values)

        value_colours = ("#562990", "#a1b2f8", "#07195d", "#135f9b", "#85e6f9",) if len(users) < 6 else (
            "#562990", "#5068c3", "#a1b2f8", "#07195d", "#135f9b", "#427faf", "#77a4cd", "#85e6f9", "#fd66cd", "#519478",)
        graph_colours = ("#aeaeb8",)

        big_angle = 2 * pi / (len(values))
        angles = pi/2 - 3*big_angle/2 - array(values.index) * big_angle

        values["start"] = angles
        values["end"] = angles + big_angle

        source = ColumnDataSource(values)

        def scale(val):
            return val+scale_factor

        def descale(val):
            return val-scale_factor

        p = figure(
            # width=800, height=800, title="",
            # tooltips=[('KSTAT', '@ksats'),]+[(u, '@{'+u+'}') for u in users],
            # tooltips=[('KSTAT', '@ksats'),('value', '@$name}')],
            toolbar_location="right", x_axis_type=None, y_axis_type=None,
            match_aspect=True, min_border=0, outline_line_color="black",
            background_fill_color="white",
        )

        ksats = p.annular_wedge(0, 0, scale(0), scale(100), "start", "end",
                                fill_color="#f2f2f2", line_color="#ffffff",
                                source=source,)

        save = SaveTool()
        hover = HoverTool(
            renderers=[ksats,],
            tooltips=[('KSAT', '@ksats'),]+[(u, '@{'+u+'}') for u in users],
        )
        p.tools = [save, hover]
        p.toolbar.autohide = True

        radii = arange(0, 101, 10)
        p.circle(0, 0, radius=radii+scale_factor,
                 fill_color=None, line_color="#ffffff")
        # p.text(
        #     0, radii+scale_factor, [str(i) for i in radii],
        #     text_font_size="12px", anchor="center",
        # )

        small_angle = big_angle / (len(users))
        for i, user in enumerate(users):
            start = angles + (i) * small_angle + small_angle * .10
            end = angles + (i + 1) * small_angle - small_angle * .10
            p.annular_wedge(
                0, 0, scale(0), scale(values[user]), start, end,
                color=value_colours[i], line_color=None, legend_label=user,
                # tooltips=[(user, values[user]),]
            )
        p.legend.click_policy = "hide"

        r = scale(radii[-1]) * 1.2
        xr = r * cos(angles + big_angle/2)
        yr = r * sin(angles + big_angle/2)
        p.text(
            xr, yr, ["\n".join(x.split()) for x in values.ksats],
            text_font_size="13px", anchor="center",
        )

        p.legend.background_fill_alpha = 0
        p.legend.glyph_width = 45
        p.legend.glyph_height = 20
        # p.legend.location = "center"
        # p.legend.location = ((p.width-p.legend.glyph_width)/2,
        #                      (p.height - p.legend.glyph_height)/2)

        p.x_range.range_padding = 0.2
        p.y_range.range_padding = 0.2

        p.grid.grid_line_color = None

        html = file_html(p, CDN, "my plot")
        name = str(uuid.uuid4())

        with open(f'/opt/app/portal-backend/media/graphs/{name}.html', 'wt') as f:
            f.write(html)
            f.flush()

        return Response(f'/media/graphs/{name}.html')

        # return Response(json_item(p))

    def post(self, request, format=None):
        scale_factor = 5

        users = request.query_params.getlist(
            'users') if 'users' in request.query_params else ("User A", "User B", "User C")
        if len(users) > 10:
            return Response("Maximum 10 users",
                            status=status.HTTP_400_BAD_REQUEST)
        dict_values = {
            'ksats': ['Knowledge of Cybersecurity', 'Ability in fork-bomb attacks', 'Skill in Kali',],
            # 'User A': [60, 90, 30],
            # 'User B': [10, 16, 99],
            # 'User C': [0, 33, 50],
        }
        for u in users:
            dict_values[u] = random.randint(0, 100, 3)

        values = DataFrame(data=dict_values)

        value_colours = ("#562990", "#a1b2f8", "#07195d", "#135f9b", "#85e6f9",) if len(users) < 6 else (
            "#562990", "#5068c3", "#a1b2f8", "#07195d", "#135f9b", "#427faf", "#77a4cd", "#85e6f9", "#fd66cd", "#519478",)
        graph_colours = ("#aeaeb8",)

        big_angle = 2 * pi / (len(values))
        angles = pi/2 - 3*big_angle/2 - array(values.index) * big_angle

        values["start"] = angles
        values["end"] = angles + big_angle

        source = ColumnDataSource(values)

        def scale(val):
            return val+scale_factor

        def descale(val):
            return val-scale_factor

        p = figure(
            # width=800, height=800, title="",
            # tooltips=[('KSTAT', '@ksats'),]+[(u, '@{'+u+'}') for u in users],
            # tooltips=[('KSTAT', '@ksats'),('value', '@$name}')],
            toolbar_location="right", x_axis_type=None, y_axis_type=None,
            match_aspect=True, min_border=0, outline_line_color="black",
            background_fill_color="white",
        )

        ksats = p.annular_wedge(0, 0, scale(0), scale(100), "start", "end",
                                fill_color="#f2f2f2", line_color="#ffffff",
                                source=source,)

        save = SaveTool()
        hover = HoverTool(
            renderers=[ksats,],
            tooltips=[('KSAT', '@ksats'),]+[(u, '@{'+u+'}') for u in users],
        )
        p.tools = [save, hover]
        p.toolbar.autohide = True

        radii = arange(0, 101, 10)
        # p.circle(0, 0, radius=radii+scale_factor,
        #          fill_color=None, line_color="#f0e1d2")
        # p.text(
        #     0, radii+scale_factor, [str(i) for i in radii],
        #     text_font_size="12px", anchor="center",
        # )

        legend_items = []
        small_angle = big_angle / 2
        for i, user in enumerate(users):
            graph = GraphRenderer()
            # graph.node_renderer.glyph = Ellipse(height=0.1, width=0.2,
            #                                     fill_color=value_colours[i])
            graph.node_renderer.glyph = Circle(radius=5,
                                               fill_color=value_colours[i],
                                               line_width=0)
            graph.node_renderer.data_source.data = dict(
                index=values.index,
                fill_color=[value_colours[i],]*len(values))
            graph.edge_renderer.data_source.data = dict(
                start=values.index,
                end=[*values.index[1:], 0])
            graph.edge_renderer.glyph.line_color = value_colours[i]
            # graph.node_renderer.fill_color = value_colours[i]
            inner_angle = angles+small_angle
            x = cos(inner_angle)*scale(values[user])
            y = sin(inner_angle)*scale(values[user])
            graph_layout = dict(zip(values.index, zip(x, y)))
            graph.layout_provider = StaticLayoutProvider(
                graph_layout=graph_layout)
            p.renderers.append(graph)
            legend_items.append(LegendItem(label=user, renderers=[
                graph.node_renderer, graph.edge_renderer]))
        legend = Legend(items=legend_items)
        p.add_layout(legend)
        p.legend.click_policy = "hide"

        r = scale(radii[-1]) * 1.2
        xr = r * cos(angles + big_angle/2)
        yr = r * sin(angles + big_angle/2)
        p.text(
            xr, yr, ["\n".join(x.split()) for x in values.ksats],
            text_font_size="13px", anchor="center",
        )

        p.legend.location = "top_left"
        p.legend.background_fill_alpha = 0
        p.legend.glyph_width = 45
        p.legend.glyph_height = 20

        p.x_range.range_padding = 0.2
        p.y_range.range_padding = 0.2

        p.grid.grid_line_color = None

        html = file_html(p, CDN, "my plot")
        name = str(uuid.uuid4())

        with open(f'/opt/app/portal-backend/media/graphs/{name}.html', 'wt') as f:
            f.write(html)
            f.flush()

        return Response(f'/media/graphs/{name}.html')

        # return Response(True)

        return Response(json_item(p))
