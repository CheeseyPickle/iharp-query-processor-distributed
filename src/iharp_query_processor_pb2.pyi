from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RasterRequest(_message.Message):
    __slots__ = ("variable", "start_datetime", "end_datetime", "temporal_resolution", "min_lat", "max_lat", "min_lon", "max_lon", "spatial_resolution", "aggregation", "file")
    VARIABLE_FIELD_NUMBER: _ClassVar[int]
    START_DATETIME_FIELD_NUMBER: _ClassVar[int]
    END_DATETIME_FIELD_NUMBER: _ClassVar[int]
    TEMPORAL_RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    MIN_LAT_FIELD_NUMBER: _ClassVar[int]
    MAX_LAT_FIELD_NUMBER: _ClassVar[int]
    MIN_LON_FIELD_NUMBER: _ClassVar[int]
    MAX_LON_FIELD_NUMBER: _ClassVar[int]
    SPATIAL_RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_FIELD_NUMBER: _ClassVar[int]
    FILE_FIELD_NUMBER: _ClassVar[int]
    variable: str
    start_datetime: str
    end_datetime: str
    temporal_resolution: str
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    spatial_resolution: float
    aggregation: str
    file: str
    def __init__(self, variable: _Optional[str] = ..., start_datetime: _Optional[str] = ..., end_datetime: _Optional[str] = ..., temporal_resolution: _Optional[str] = ..., min_lat: _Optional[float] = ..., max_lat: _Optional[float] = ..., min_lon: _Optional[float] = ..., max_lon: _Optional[float] = ..., spatial_resolution: _Optional[float] = ..., aggregation: _Optional[str] = ..., file: _Optional[str] = ...) -> None: ...

class RasterResponse(_message.Message):
    __slots__ = ("pickled_arr",)
    PICKLED_ARR_FIELD_NUMBER: _ClassVar[int]
    pickled_arr: bytes
    def __init__(self, pickled_arr: _Optional[bytes] = ...) -> None: ...
