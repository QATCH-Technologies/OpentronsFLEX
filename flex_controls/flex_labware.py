import json
from typing import List, Dict, Any
from flex_constants import FlexDeckLocations


class Ordering:
    def __init__(self, ordering: List[List[str]]):
        self.ordering = ordering


class Brand:
    def __init__(self, brand: str, brandId: List[str]):
        self.brand = brand
        self.brand_id = brandId


class Metadata:
    def __init__(self, displayName: str, displayCategory: str, displayVolumeUnits: str, tags: List[str]):
        self.display_name = displayName
        self.display_category = displayCategory
        self.display_volume_units = displayVolumeUnits
        self.tags = tags

    def get_display_name(self):
        return self.display_name

    def get_display_name(self):
        return self.display_name


class Dimensions:
    def __init__(self, xDimension: float, yDimension: float, zDimension: float):
        self.x_dimension = xDimension
        self.y_dimension = yDimension
        self.z_dimension = zDimension


class Well:
    def __init__(self, depth: float, totalLiquidVolume: float, shape: str, diameter: float, x: float, y: float, z: float):
        self.depth = depth
        self.total_liquid_volume = totalLiquidVolume
        self.shape = shape
        self.diameter = diameter
        self.x = x
        self.y = y
        self.z = z


class Wells:
    def __init__(self, wells: Dict[str, Any]):
        self.wells = {key: Well(**value) for key, value in wells.items()}


class GroupMetadata:
    def __init__(self, wellBottomShape: str):
        self.well_bottom_shape = wellBottomShape


class Group:
    def __init__(self, metadata: Dict[str, str], wells: List[str]):
        self.metadata = GroupMetadata(**metadata)
        self.wells = wells


class Parameters:
    def __init__(self, format: str, quirks: List[str], isTiprack: bool, isMagneticModuleCompatible: bool, loadName: str):
        self.format = format
        self.quirks = quirks
        self.is_tiprack = isTiprack
        self.is_magnetic_module_compatible = isMagneticModuleCompatible
        self.load_name = loadName

    def get_load_name(self) -> str:
        return self.load_name


class CornerOffsetFromSlot:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def get_offsets(self) -> dict:
        return {"x": self._get_x(), "y": self._get_y(), "z": self._get_z()}

    def _get_x(self):
        return self.x

    def _get_y(self):
        return self.y

    def _get_z(self):
        return self.z


class StackingOffsetWithLabware:
    def __init__(self, stackingOffsetWithLabware: Dict[str, Dict[str, float]]):
        self.stackingOffsetWithLabware = stackingOffsetWithLabware


class FlexLabware:
    def __init__(self, location: FlexDeckLocations, file_path: str):
        self.data = self.load_json(file_path)
        self.set_id(id)
        self.set_location(location)
        self.ordering = Ordering(self.data["ordering"])
        self.brand = Brand(**self.data["brand"])
        self.metadata = Metadata(**self.data["metadata"])
        self.dimensions = Dimensions(**self.data["dimensions"])
        self.wells = Wells(self.data["wells"])
        self.groups = [Group(**group) for group in self.data["groups"]]
        self.parameters = Parameters(**self.data["parameters"])
        self.namespace = self.data["namespace"]
        self.version = self.data["version"]
        self.schema_version = self.data["schemaVersion"]
        self.corner_offset_from_slot = CornerOffsetFromSlot(
            **self.data["cornerOffsetFromSlot"])
        self.stacking_offset_with_labware = StackingOffsetWithLabware(
            self.data["stackingOffsetWithLabware"])

    # --- Mutator Methods --- #
    def set_id(self, id: int) -> None:
        self._id = id

    def set_location(self, location: FlexDeckLocations) -> None:
        self._location = location

    # --- Accessor Methods --- #

    def get_offsets(self) -> dict:
        return self.corner_offset_from_slot.get_offsets()

    def get_id(self) -> int:
        return self._id

    def get_location(self) -> FlexDeckLocations:
        return self._location

    def get_display_name(self) -> str:
        return self.metadata.display_name

    def get_load_name(self) -> str:
        return self.parameters.get_load_name()

    def get_namespace(self) -> str:
        return self.namespace

    def get_version(self) -> int:
        return self.version

    def is_tiprack(self):
        return self.parameters.is_tiprack

    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as f:
            return json.load(f)


# Usage Example
if __name__ == "__main__":
    parser = FlexLabware(
        r'C:\Users\paulm\dev\OpentronsFLEX\labware\nanovis_q_4x6.json')
    print(parser.brand.brand)  # Example: Access the "brand" field
    print(parser.wells.wells["A1"].x)  # Example: Access well A1's x coordinate
