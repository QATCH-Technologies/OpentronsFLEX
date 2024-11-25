import json
from typing import List, Dict, Any
from flex_constants import FlexLocations


class Ordering:
    def __init__(self, ordering: List[List[str]]):
        self.ordering = ordering


class Brand:
    def __init__(self, brand: str, brand_id: List[str]):
        self.brand = brand
        self.brand_id = brand_id


class Metadata:
    def __init__(self, display_name: str, display_category: str, display_volume_units: str, tags: List[str]):
        self.display_name = display_name
        self.display_category = display_category
        self.display_volume_units = display_volume_units
        self.tags = tags

    def get_display_name(self):
        return self.display_name

    def get_display_name(self):
        return self.display_name


class Dimensions:
    def __init__(self, x_dimension: float, y_dimension: float, z_dimension: float):
        self.x_dimension = x_dimension
        self.y_dimension = y_dimension
        self.z_dimension = z_dimension


class Well:
    def __init__(self, depth: float, total_liquid_volume: float, shape: str, diameter: float, x: float, y: float, z: float):
        self.depth = depth
        self.total_liquid_volume = total_liquid_volume
        self.shape = shape
        self.diameter = diameter
        self.x = x
        self.y = y
        self.z = z


class Wells:
    def __init__(self, wells: Dict[str, Any]):
        self.wells = {key: Well(**value) for key, value in wells.items()}


class GroupMetadata:
    def __init__(self, well_bottom_shape: str):
        self.well_bottom_shape = well_bottom_shape


class Group:
    def __init__(self, metadata: Dict[str, str], wells: List[str]):
        self.metadata = GroupMetadata(**metadata)
        self.wells = wells


class Parameters:
    def __init__(self, format: str, quirks: List[str], is_tiprack: bool, is_magnetic_module_compatible: bool, load_name: str):
        self.format = format
        self.quirks = quirks
        self.is_tiprack = is_tiprack
        self.is_magnetic_module_compatible = is_magnetic_module_compatible
        self.load_name = load_name

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
    def __init__(self, id: int, location: FlexLocations, file_path: str):
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

    def set_location(self, location: FlexLocations) -> None:
        self._location = location

    # --- Accessor Methods --- #

    def get_offsets(self) -> dict:
        return self.corner_offset_from_slot.get_offsets()

    def get_id(self) -> int:
        return self._id

    def get_location(self) -> FlexLocations:
        return self._location

    def get_display_name(self) -> str:
        return self.metadata.displayName

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
