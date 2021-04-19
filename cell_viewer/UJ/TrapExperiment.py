import pathlib
from dataclasses import dataclass, fields
from pathlib import Path
from typing import AnyStr, Callable, Iterable

from dask_image.imread import imread


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

        def read_tif(path: Path, compute: bool):
            image = imread(str(path.joinpath("*.tif")))
            return image if not compute else image.compute()

        return self._read_chunked_data(
            search_on=search_on,
            func=read_tif,
            file_glob="*.tif",
            compute=compute
        )

    def _read_chunked_data(
        self,
        search_on: Iterable[AnyStr],
        func: Callable,
        file_glob: AnyStr,
        **kwargs
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
                directory.name:
                func(path=directory, **kwargs)
                for directory in dirs_with_data
            }

            data_dict[field.name] = readed_data
            
        return data_dict