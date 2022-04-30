from __future__ import annotations
from dataclasses import dataclass

import matplotlib as mpl

from seaborn._marks.base import Mark, Mappable

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Union, Any
    from matplotlib.artist import Artist
    from seaborn._core.scales import Scale

    MappableBool = Union[bool, Mappable]
    MappableFloat = Union[float, Mappable]
    MappableString = Union[str, Mappable]
    MappableColor = Union[str, tuple, Mappable]  # TODO


@dataclass
class Bar(Mark):
    """
    An interval mark drawn between baseline and data values with a width.
    """
    color: MappableColor = Mappable("C0", groups=True)
    alpha: MappableFloat = Mappable(1, groups=True)
    edgecolor: MappableColor = Mappable(depend="color", groups=True)
    edgealpha: MappableFloat = Mappable(depend="alpha", groups=True)
    edgewidth: MappableFloat = Mappable(rc="patch.linewidth")
    fill: MappableBool = Mappable(True, groups=True)
    # pattern: MappableString = Mappable(None, groups=True)  # TODO no Semantic yet

    width: MappableFloat = Mappable(.8)  # TODO groups?
    baseline: MappableFloat = Mappable(0)  # TODO *is* this mappable?

    def resolve_properties(self, data, scales):

        # TODO copying a lot from scatter

        resolved = super().resolve_properties(data, scales)

        resolved["facecolor"] = self._resolve_color(data, "", scales)
        resolved["edgecolor"] = self._resolve_color(data, "edge", scales)

        fc = resolved["facecolor"]
        if isinstance(fc, tuple):
            resolved["facecolor"] = fc[0], fc[1], fc[2], fc[3] * resolved["fill"]
        else:
            fc[:, 3] = fc[:, 3] * resolved["fill"]  # TODO Is inplace mod a problem?
            resolved["facecolor"] = fc

        return resolved

    def plot(self, split_gen, scales, orient):

        def coords_to_geometry(x, y, w, b):
            # TODO possible too slow with lots of bars (e.g. dense hist)
            # Why not just use BarCollection?
            if orient == "x":
                w, h = w, y - b
                xy = x - w / 2, b
            else:
                w, h = x - b, w
                xy = b, y - h / 2
            return xy, w, h

        for keys, data, ax in split_gen():

            xys = data[["x", "y"]].to_numpy()
            data = self.resolve_properties(data, scales)

            bars = []
            for i, (x, y) in enumerate(xys):

                baseline = data["baseline"][i]
                width = data["width"][i]
                xy, w, h = coords_to_geometry(x, y, width, baseline)

                bar = mpl.patches.Rectangle(
                    xy=xy,
                    width=w,
                    height=h,
                    facecolor=data["facecolor"][i],
                    edgecolor=data["edgecolor"][i],
                    linewidth=data["edgewidth"][i],
                )
                ax.add_patch(bar)
                bars.append(bar)

            # TODO add container object to ax, line ax.bar does

    def _legend_artist(
        self, variables: list[str], value: Any, scales: dict[str, Scale],
    ) -> Artist:
        # TODO return some sensible default?
        key = {v: value for v in variables}
        key = self.resolve_properties(key, scales)
        artist = mpl.patches.Patch(
            facecolor=key["facecolor"],
            edgecolor=key["edgecolor"],
            linewidth=key["edgewidth"],
        )
        return artist
