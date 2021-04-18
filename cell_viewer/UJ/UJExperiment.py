from collections import defaultdict
from cell_viewer.UJ.TrapExperiment import (
    Path,
    TrapExperiment,
)

from dataclasses import (
    dataclass,
    field,
)

from typing import (
    AnyStr,
    List,
    Union,
)

import pathlib

@dataclass
class UJExperiment:
    name: str
    path: Path
    _path: Path = field(init=False, repr=False)

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, path: Union[AnyStr, Path]) -> None:

        if isinstance(path, str):
            path = pathlib.Path(path)

        if isinstance(path, (pathlib.PosixPath, pathlib.WindowsPath)):
            self._path = path

            for PATH in self._PATHS:
                setattr(self, PATH, path.joinpath(PATH))
        else:
            raise ValueError()

    @property
    def _PATHS(self) -> List:
        return [
            "data",
            "data_cells",
            "data_cells_tracked",
            "data_masks",
            "data_raw",
            "data_rois",
            "data_segmentable",
            "data_tif",
            "figures"
        ]

    def trap_data(self, trap_glob: AnyStr):

        Traps = defaultdict(TrapExperiment)

        for path in self.path.glob(f"data_*{self.path.anchor}{trap_glob}"):
            if path.is_dir():
                setattr(Traps[path.name], path.parent.name, path)

        return Traps