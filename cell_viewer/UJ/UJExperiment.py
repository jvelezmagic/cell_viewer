from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import AnyStr, List, Union

from cell_viewer.UJ.TrapExperiment import TrapExperiment


@dataclass
class UJExperiment:
    """Class to access to UJExperiment data directly.
    """

    name: str
    path: Path
    _path: Path = field(init=False, repr=False)

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, path: Union[AnyStr, Path]) -> None:

        if isinstance(path, str):
            path = Path(path)

        if isinstance(path, Path):
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
            "figures",
        ]

    def trap_data(self, trap_glob: AnyStr):

        Traps = defaultdict(TrapExperiment)

        for data_path in self.path.glob("data_*"):
            if data_path.is_dir():
                for trap_path in data_path.glob(trap_glob):
                    if trap_path.is_dir():
                        setattr(Traps[trap_path.name], data_path.name, trap_path)

        return Traps
