# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: iharp_query_processor.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'iharp_query_processor.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1biharp_query_processor.proto\"\xef\x01\n\rRasterRequest\x12\x10\n\x08variable\x18\x01 \x01(\t\x12\x16\n\x0estart_datetime\x18\x02 \x01(\t\x12\x14\n\x0c\x65nd_datetime\x18\x03 \x01(\t\x12\x1b\n\x13temporal_resolution\x18\x04 \x01(\t\x12\x0f\n\x07min_lat\x18\x05 \x01(\x02\x12\x0f\n\x07max_lat\x18\x06 \x01(\x02\x12\x0f\n\x07min_lon\x18\x07 \x01(\x02\x12\x0f\n\x07max_lon\x18\x08 \x01(\x02\x12\x1a\n\x12spatial_resolution\x18\t \x01(\x02\x12\x13\n\x0b\x61ggregation\x18\n \x01(\t\x12\x0c\n\x04\x66ile\x18\x0b \x01(\t\"%\n\x0eRasterResponse\x12\x13\n\x0bpickled_arr\x18\x01 \x01(\x0c\x32\x38\n\x06\x44\x42Node\x12.\n\tGetRaster\x12\x0e.RasterRequest\x1a\x0f.RasterResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'iharp_query_processor_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_RASTERREQUEST']._serialized_start=32
  _globals['_RASTERREQUEST']._serialized_end=271
  _globals['_RASTERRESPONSE']._serialized_start=273
  _globals['_RASTERRESPONSE']._serialized_end=310
  _globals['_DBNODE']._serialized_start=312
  _globals['_DBNODE']._serialized_end=368
# @@protoc_insertion_point(module_scope)
