import ast
from dataclasses import dataclass, fields
from pathlib import Path
from typing import AnyStr, Callable, Iterable

import janitor
import numpy as np
import pandas as pd
import shapely.geometry as geometry
import shapely.ops
from dask_image.imread import imread


@dataclass
class TrapExperiment:
    """Class to access to traps data directly.
    """

    data_cells: Path = None
    data_cells_tracked: Path = None
    data_mask: Path = None
    data_raw: Path = None
    data_rois: Path = None
    data_segmentable: Path = None
    data_tif: Path = None

    def read_tifs(self, search_on: Iterable[AnyStr] = None, compute: bool = False):
        def read_tif(path: Path, compute: bool):
            image = imread(str(path.joinpath("*.tif")))
            return image if not compute else image.compute()

        return self._read_chunked_data(
            search_on=search_on, func=read_tif, file_glob="*.tif", compute=compute
        )

    def read_cells(self, search_on: Iterable[AnyStr] = None):
        def read_cells(path: Path):

            roi_files = sorted(path.glob("*.pkl"))

            return (
                pd.DataFrame(
                    dict(list_str_cells=[pd.read_pickle(file) for file in roi_files])
                )
                # Each observation is a list of strings.
                # Convertet to long format.
                .explode(column="list_str_cells")
                # Each string is a set of variables delimited by tab.
                .list_str_cells.str.rstrip("\t")  # Get pandas series.
                .str.split(r"\t+", expand=True)  # One column per variable.
                .reset_index()
                # Indicate actual column values.
                .rename_columns(
                    {
                        "index": "frame",
                        0: "id",  #  cellID
                        1: "color",  # cellColor
                        2: "roi_id",  # roiID
                        3: "track_id",  # trackID
                        4: "roi_polygon",  # roiPoly
                        5: "center",  # center
                        6: "axis",  # axis
                        7: "GFP",  # GFP
                        8: "DsRed",  # DsRed
                        9: "state",  # state
                        10: "previous_frame",  # trackedBy_previous_frame
                        11: "next_frame",  # trackedBy_next_frame
                        12: "tracking_score",  # tracking_score
                        13: "mother_id",  # motherID
                    }
                )
                #  Transfrom shape-strings columns into geometries.
                .assign(
                    roi_polygon=lambda df: df.roi_polygon.apply(ast.literal_eval).apply(
                        geometry.Polygon
                    ),
                    center=lambda df: df.center.apply(ast.literal_eval).apply(
                        geometry.Point
                    ),
                    axis=lambda df: df.axis.apply(ast.literal_eval).apply(
                        geometry.LineString
                    ),
                )
                #  Swap coordinates since napari and ImageJ has inverted axes.
                .assign(
                    roi_polygon=lambda df: df.roi_polygon.apply(
                        lambda polygon: shapely.ops.transform(
                            lambda x, y: (y, x), polygon
                        )
                    )
                )
                # Transform polygons to fit napari conditions.
                .assign(
                    napari_polygon=lambda df: df.apply(
                        lambda df_row: np.array(
                            [
                                [df_row.frame, x, y]
                                for (x, y) in df_row.roi_polygon.exterior.coords
                            ]
                        ),
                        axis=1,
                    )
                )
                .assign(
                    id=lambda df: df.id.str.split(".").apply(lambda x: x[1]).astype(int)
                    + 1,
                    coords=lambda df: df.roi_polygon.apply(
                        lambda x: np.array(x.exterior.coords)
                    ),
                )
            )

        return self._read_chunked_data(
            search_on=search_on, func=read_cells, file_glob="*.pkl"
        )

    def _read_chunked_data(
        self, search_on: Iterable[AnyStr], func: Callable, file_glob: AnyStr, **kwargs
    ):

        data_dict = dict()
        for field in fields(self):

            field_value = getattr(self, field.name)

            # Skip if field is not intended to search on.
            if search_on is not None and field.name not in search_on:
                continue

            # Skip if field is not a Path object
            if not isinstance(field_value, Path):
                continue

            # Identify directories that contains files of interest.
            dirs_with_data = {path.parent for path in field_value.rglob(file_glob)}

            # Read each directory into something specified by `func`.
            readed_data = {
                directory.name: func(path=directory, **kwargs)
                for directory in dirs_with_data
            }

            data_dict[field.name] = readed_data

        return data_dict
