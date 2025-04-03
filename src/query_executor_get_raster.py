from datetime import datetime
import math
import cdsapi
import pandas as pd
import xarray as xr

import pickle
import grpc
import iharp_query_processor_pb2
import iharp_query_processor_pb2_grpc

import threading

from .query_executor import QueryExecutor
from .utils.const import time_resolution_to_freq

MAX_MESSAGE_LENGTH = 2147483647

class GetRasterExecutor(QueryExecutor):
    def __init__(
        self,
        variable: str,
        start_datetime: str,
        end_datetime: str,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        temporal_resolution: str,  # e.g., "hour", "day", "month", "year"
        spatial_resolution: float,  # e.g., 0.25, 0.5, 1.0
        aggregation,  # e.g., "mean", "max", "min"
        metadata=None,  # metadata file path
    ):
        super().__init__(
            variable,
            start_datetime,
            end_datetime,
            min_lat,
            max_lat,
            min_lon,
            max_lon,
            temporal_resolution,
            spatial_resolution,
            aggregation,
            metadata=metadata,
        )

    def _check_metadata(self):
        """
        Return: [local_files], [api_calls]
        """
        df_overlap, leftover = self.metadata.query_get_overlap_and_leftover(
            self.variable,
            self.start_datetime,
            self.end_datetime,
            self.min_lat,
            self.max_lat,
            self.min_lon,
            self.max_lon,
            self.temporal_resolution,
            self.spatial_resolution,
            self.aggregation,
        )
        assert leftover is None, "Should not have leftover in experiment"

        file_paths = df_overlap["file_path"].tolist()
        file_hosts = df_overlap["host"].tolist()
        local_files = list(zip(file_paths, file_hosts))

        api_calls = []
        if leftover is not None:
            leftover_min_lat = math.floor(leftover.latitude.min().item())
            leftover_max_lat = math.ceil(leftover.latitude.max().item())
            leftover_min_lon = math.floor(leftover.longitude.min().item())
            leftover_max_lon = math.ceil(leftover.longitude.max().item())
            leftover_start_datetime = pd.Timestamp(leftover.time.min().item())
            leftover_end_datetime = pd.Timestamp(leftover.time.max().item())
            leftover_start_year, leftover_start_month, leftover_start_day = (
                leftover_start_datetime.year,
                leftover_start_datetime.month,
                leftover_start_datetime.day,
            )
            leftover_end_year, leftover_end_month, leftover_end_day = (
                leftover_end_datetime.year,
                leftover_end_datetime.month,
                leftover_end_datetime.day,
            )

            years = [str(i) for i in range(leftover_start_year, leftover_end_year + 1)]
            months = [str(i).zfill(2) for i in range(1, 13)]
            days = [str(i).zfill(2) for i in range(1, 32)]
            if self.temporal_resolution == "month":
                if leftover_start_year == leftover_end_year:
                    months = [str(i).zfill(2) for i in range(leftover_start_month, leftover_end_month + 1)]
            if self.temporal_resolution == "day" or self.temporal_resolution == "hour":
                if leftover_start_year == leftover_end_year:
                    months = [str(i).zfill(2) for i in range(leftover_start_month, leftover_end_month + 1)]
                    if leftover_start_month == leftover_end_month:
                        days = [str(i).zfill(2) for i in range(leftover_start_day, leftover_end_day + 1)]

            dataset = "reanalysis-era5-single-levels"
            request = {
                "product_type": ["reanalysis"],
                "variable": [self.variable],
                "year": years,
                "month": months,
                "day": days,
                "time": [f"{str(i).zfill(2)}:00" for i in range(0, 24)],
                "data_format": "netcdf",
                "download_format": "unarchived",
                "area": [leftover_max_lat, leftover_min_lon, leftover_min_lat, leftover_max_lon],
            }
            api_calls.append((dataset, request))
        local_files = sorted(local_files)
        print("local files:", local_files)
        print("api:", api_calls)
        return local_files, api_calls

    def _gen_download_file_name(self):
        dt = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"download_{dt}.nc"
    
    def query_node(self, file, host, ds_list, lock):
        # TODO: make TOML file to also store port nums
        with grpc.insecure_channel(
                f'{host}:50051',
                options=[
                    ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
                    ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
                ]) as channel:
            stub = iharp_query_processor_pb2_grpc.DBNodeStub(channel)
            response = stub.GetRaster(iharp_query_processor_pb2.RasterRequest(
                variable = self.variable,
                start_datetime = self.start_datetime,
                end_datetime = self.end_datetime,
                temporal_resolution = self.temporal_resolution,
                min_lat = self.min_lat,
                max_lat = self.max_lat,
                min_lon = self.min_lon,
                max_lon = self.max_lon,
                spatial_resolution = self.spatial_resolution,
                aggregation = self.aggregation,
                file = file
            ))

        ds = pickle.loads(response.pickled_arr)
        with lock:
            ds_list.append(ds)

    def execute(self):
        # 1. check metadata
        file_list, api = self._check_metadata()

        # 2. call apis
        download_file_list = []
        if api:
            c = cdsapi.Client()
            for dataset, request in api:
                file_name = self._gen_download_file_name()
                c.retrieve(dataset, request).download(file_name)
                download_file_list.append(file_name)

        # 3. execute query
        ds_list = []
        for file in download_file_list:
            ds = xr.open_dataset(file, engine="netcdf4")
            # drop unused variables
            # if "number" in ds.coords:
            #     ds = ds.drop_vars("number")
            # if "expver" in ds.coords:
            #     ds = ds.drop_vars("expver")
            ds = ds.sel(
                time=slice(self.start_datetime, self.end_datetime),
                latitude=slice(self.max_lat, self.min_lat),
                longitude=slice(self.min_lon, self.max_lon),
            )
            # temporal resample
            if self.temporal_resolution != "hour":
                resampled = ds.resample(time=time_resolution_to_freq(self.temporal_resolution))
                if self.aggregation == "mean":
                    ds = resampled.mean()
                elif self.aggregation == "max":
                    ds = resampled.max()
                elif self.aggregation == "min":
                    ds = resampled.min()
                else:
                    raise ValueError("Invalid temporal_aggregation")
            # spatial resample
            if self.spatial_resolution > 0.25:
                c_f = int(self.spatial_resolution / 0.25)
                coarsened = ds.coarsen(latitude=c_f, longitude=c_f, boundary="trim")
                if self.aggregation == "mean":
                    ds = coarsened.mean()
                elif self.aggregation == "max":
                    ds = coarsened.max()
                elif self.aggregation == "min":
                    ds = coarsened.min()
                else:
                    raise ValueError("Invalid spatial_aggregation")
            ds_list.append(ds)

        # 3.2 Call nodes and get input 
        query_threads : list[threading.Thread] = []
        lock = threading.Lock()
        for file, host in file_list:
            thread = threading.Thread(target=self.query_node, args=[file, host, ds_list, lock])
            query_threads.append(thread)
            thread.start()
        
        for thread in query_threads:
            thread.join()


        # 3.3 assemble result
        # ds = xr.concat([i.chunk() for i in ds_list], dim="time")
        # compat="override" is a temporal walkaround as pre-aggregation value conflicts with downloaded data
        # future solution: use new encoding when write pre-aggregated data
        try:
            ds = xr.merge([i.chunk() for i in ds_list], compat="no_conflicts")
        except ValueError:
            print("WARNING: conflict in merging data, use override")
            ds = xr.merge([i.chunk() for i in ds_list], compat="override")

        return ds.compute()
