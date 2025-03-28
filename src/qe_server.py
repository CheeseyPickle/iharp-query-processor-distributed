from concurrent import futures
import logging

import sys
import pickle
import grpc
import iharp_query_processor_pb2
import iharp_query_processor_pb2_grpc

import xarray as xr
from .utils.const import time_resolution_to_freq

class DBNode(iharp_query_processor_pb2_grpc.DBNodeServicer):
    def GetRaster(self, request, context):
        ds = xr.open_dataset(request.file, engine="netcdf4").sel(
                time=slice(request.start_datetime, request.end_datetime),
                latitude=slice(request.max_lat, request.min_lat),
                longitude=slice(request.min_lon, request.max_lon),
            )
        
        # temporal resample
        if request.temporal_resolution != "hour":
            resampled = ds.resample(time=time_resolution_to_freq(request.temporal_resolution))
            if request.aggregation == "mean":
                ds = resampled.mean()
            elif request.aggregation == "max":
                ds = resampled.max()
            elif request.aggregation == "min":
                ds = resampled.min()
            else:
                raise ValueError("Invalid temporal_aggregation")
        # spatial resample
        if request.spatial_resolution > 0.25:
            c_f = int(request.spatial_resolution / 0.25)
            coarsened = ds.coarsen(latitude=c_f, longitude=c_f, boundary="trim")
            if request.aggregation == "mean":
                ds = coarsened.mean()
            elif request.aggregation == "max":
                ds = coarsened.max()
            elif request.aggregation == "min":
                ds = coarsened.min()
            else:
                raise ValueError("Invalid spatial_aggregation")

        # Dump into pickle
        # As long as pickle file is less than ~4.29 GB (2^32 bytes), we can send it
        pickled_arr = pickle.dumps(ds) 
        return iharp_query_processor_pb2.RasterResponse(pickled_arr=pickled_arr)



def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    iharp_query_processor_pb2_grpc.add_DBNodeServicer_to_server(DBNode(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    if len(sys.argv) > 2:
        print("Usage: python dbnode_server.py [Port Number]")
    elif len(sys.argv) == 2:
        port = sys.argv[1]
    else:
        # TODO: Read this from a TOML file probably?
        port = "50051"
    serve(port)