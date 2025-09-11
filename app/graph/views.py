import logging
import secrets

from bokeh.embed import file_html
from bokeh.models import (ColumnDataSource, HoverTool, SaveTool)
from bokeh.plotting import figure
from bokeh.resources import CDN
from numpy import arange, array, cos, pi, sin
from pandas import DataFrame
from rest_framework import permissions, status, views
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response

from external.models import LearnerRecord

logger = logging.getLogger(__name__)


class GraphView(views.APIView):
    """
    Generate Bokeh Graphs
    """
    queryset = LearnerRecord.objects.all()
    permission_classes = [permissions.AllowAny]
    renderer_classes = [StaticHTMLRenderer,]

    def get(self, request, format=None):
        scale_factor = 40

        users = request.query_params.getlist(
            'users') if 'users' in request.query_params else (
            "User A", "User B", "User C")
        if len(users) > 10:
            return Response("Maximum 10 users",
                            status=status.HTTP_400_BAD_REQUEST)
        logger.info("graph %s", users)
        dict_values = {
            'ksats': ['Knowledge of Cybersecurity',
                      'Ability in fork-bomb attacks', 'Skill in Kali',],
            # 'User A': [60, 90, 30],
            # 'User B': [10, 16, 99],
            # 'User C': [0, 33, 50],
        }
        for u in users:
            dict_values[u] = [secrets.randbelow(100) for _ in range(3)]

        values = DataFrame(data=dict_values)

        value_colours = (
            ("#562990", "#a1b2f8", "#07195d", "#135f9b", "#85e6f9")
            if len(users) < 6 else
            ("#562990", "#5068c3", "#a1b2f8", "#07195d", "#135f9b",
             "#427faf", "#77a4cd", "#85e6f9", "#fd66cd", "#519478")
        )

        big_angle = 2 * pi / (len(values))
        angles = pi/2 - 3*big_angle/2 - array(values.index) * big_angle

        values["start"] = angles
        values["end"] = angles + big_angle

        source = ColumnDataSource(values)

        def scale(val):
            return val+scale_factor

        p = figure(
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
            tooltips=[('KSTAT', '@ksats'),]+[(u, '@{'+u+'}') for u in users],
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

        p.x_range.range_padding = 0.2
        p.y_range.range_padding = 0.2

        p.grid.grid_line_color = None

        html = file_html(p, CDN, "my plot")

        return Response(html)
