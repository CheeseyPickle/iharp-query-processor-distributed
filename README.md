# iharp-query-processor-distributed

## Modifying the project

If you ever change the .proto files, you need to use gRPC to update some of the .py files. 

Run `cd src` and `python -m grpc_tools.protoc -I../protos --python_out=. --pyi_out=. --grpc_python_out=. ../protos/iharp_query_processor.proto` in order to do so. This calls gRPC to regenerate the communication files (the .py/.pyi files with `pb2` in them).