from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field, fields
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

        # for _path in self._PATHS:

        #     if not _path.startswith("data_"):
        #         continue

        #     field_path = getattr(self, _path)

        #     if not field_path.exists():
        #         continue

        #     for path in field_path.glob(trap_glob):
        #         print(path, path.exists(), path.is_dir())
        #         if path.is_dir():
        #             setattr(Traps[path.name], path.parent.name, path)

        for path in self.path.glob(f"data_*{self.path.anchor}{trap_glob}"):
            if path.is_dir():
                setattr(Traps[path.name], path.parent.name, path)

        return Traps
