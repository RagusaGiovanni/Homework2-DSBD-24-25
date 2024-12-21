# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: auth.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'auth.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nauth.proto\"W\n\x0f\x41uthUserRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x0e\n\x06ticker\x18\x02 \x01(\t\x12\x12\n\nhigh_value\x18\x03 \x01(\x01\x12\x11\n\tlow_value\x18\x04 \x01(\x01\"u\n\x15\x41uthUserUpdateRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x12\n\nold_ticker\x18\x02 \x01(\t\x12\x12\n\nnew_ticker\x18\x03 \x01(\t\x12\x12\n\nhigh_value\x18\x04 \x01(\x01\x12\x11\n\tlow_value\x18\x05 \x01(\x01\"L\n\x14\x41uthThresholdRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x12\n\nhigh_value\x18\x02 \x01(\x01\x12\x11\n\tlow_value\x18\x03 \x01(\x01\"\"\n\x10\x41uthUserResponse\x12\x0e\n\x06status\x18\x01 \x01(\t2\xec\x01\n\x0b\x41uthService\x12\x33\n\x0cRegisterUser\x12\x10.AuthUserRequest\x1a\x11.AuthUserResponse\x12\x37\n\nUpdateUser\x12\x16.AuthUserUpdateRequest\x1a\x11.AuthUserResponse\x12<\n\x10UpdateThresholds\x12\x15.AuthThresholdRequest\x1a\x11.AuthUserResponse\x12\x31\n\nDeleteUser\x12\x10.AuthUserRequest\x1a\x11.AuthUserResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'auth_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_AUTHUSERREQUEST']._serialized_start=14
  _globals['_AUTHUSERREQUEST']._serialized_end=101
  _globals['_AUTHUSERUPDATEREQUEST']._serialized_start=103
  _globals['_AUTHUSERUPDATEREQUEST']._serialized_end=220
  _globals['_AUTHTHRESHOLDREQUEST']._serialized_start=222
  _globals['_AUTHTHRESHOLDREQUEST']._serialized_end=298
  _globals['_AUTHUSERRESPONSE']._serialized_start=300
  _globals['_AUTHUSERRESPONSE']._serialized_end=334
  _globals['_AUTHSERVICE']._serialized_start=337
  _globals['_AUTHSERVICE']._serialized_end=573
# @@protoc_insertion_point(module_scope)