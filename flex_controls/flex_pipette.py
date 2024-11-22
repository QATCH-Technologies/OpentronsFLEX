from flex_constants import FlexPipettes, FlexMountPositions


class FlexPipette:
    def __init__(self, pipette: FlexPipettes, mount_position: FlexMountPositions) -> None:
        self.id = None
        self._set_pipette(pipette)
        self._set_mount_position(mount_position)

    def _is_valid_pipette(self, pipette) -> bool:
        return True if pipette in FlexPipettes else False

    def _is_valid_mount_position(self, mount_position) -> bool:
        return True if mount_position in FlexMountPositions else False

    def set_pipette_id(self, id) -> None:
        self.id = id

    def _set_pipette(self, pipette: FlexPipettes) -> None:
        if self._is_valid_pipette(pipette=pipette):
            self._pipette = pipette
        else:
            raise ValueError(f"Invalid pipette tip {pipette.value}.")

    def _set_mount_position(self, mount_position: FlexMountPositions) -> None:
        if self._is_valid_mount_position(mount_position=mount_position):
            self._mount_position = mount_position
        else:
            raise ValueError(f"Invalid mount position {mount_position.value}.")

    def _get_pipette(self) -> str:
        return self._pipette.value

    def _get_mount_position(self) -> str:
        return self._mount_position.value
