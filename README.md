# iharp-query-processor-distributed

## Modifying the project

If you ever change the .proto files, you need to use gRPC to update some of the .py files. 

Run `cd src` and `python -m grpc_tools.protoc -I../protos --python_out=. --pyi_out=. --grpc_python_out=. ../protos/iharp_query_processor.proto` in order to do so. This calls gRPC to regenerate the communication files (the .py/.pyi files with `pb2` in them).

## Communication

Communication between the head node and the database nodes is done via gRPC. The data is pickled and sent over the network. For this to work the database nodes and the head node all have to run the same version of Python (or at least versions where pickling is the same between them).