from dataclasses import dataclass, fields
from dask_image.imread import imread
from typing import (
    AnyStr,
    Union,
    Iterable,
)

#from skimage.io import Image

import pathlib

Path = Union[pathlib.PosixPath, pathlib.WindowsPath]

@dataclass
class TrapExperiment:
    data_cells: Path = None
    data_cells_tracked: Path = None
    data_mask: Path = None
    data_raw: Path = None
    data_rois: Path = None
    data_segmentable: Path = None
    data_tif: Path = None

    def read_tifs(self, search_on: Iterable[AnyStr] = None, compute: bool = False):

        tifs = dict()
        for field in fields(self):

            if search_on is not None and field.name not in search_on:
                continue

            attr = getattr(self, field.name)

            def read_tif(path: Path, compute: bool = False):
                image = imread(str(path.joinpath("*.tif")))

                return image if not compute else image.compute()

            if isinstance(attr, (pathlib.PosixPath, pathlib.WindowsPath)):
                paths = {
                    path.parent.name:
                    read_tif(path = path.parent, compute = compute)
                    for path in attr.rglob("*.tif")
                }

                tifs[field.name] = paths

        return tifs