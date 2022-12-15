#!/usr/bin/env python
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
# NOTICE: THIS FILE HAS BEEN MODIFIED BY INTEL CORPORATION UNDER COMPLIANCE
# WITH THE APACHE 2.0 LICENSE FROM THE ORIGINAL WORK
#

from concurrent import futures
from importlib import import_module
import logging
import inspect
import grpc
import qmp
import os
from grpc_reflection.v1alpha import reflection
import frontend_virtio_blk_pb2
import frontend_virtio_blk_pb2_grpc
import frontend_nvme_pcie_pb2
import frontend_nvme_pcie_pb2_grpc
import backend_nvme_tcp_pb2
import backend_nvme_tcp_pb2_grpc


class PassThroughGrpcCallFunctor:
    def __init__(self, method_name, opi_service_address, client_class) -> None:
        self._method_name = method_name
        self._opi_service_address = opi_service_address
        self._client_class = client_class

    def __call__(self, request, context):
        logging.info(
            f"Passing through `{self._method_name}` with `{request}` and `{context}`"
        )
        with grpc.insecure_channel(self._opi_service_address) as channel:
            client = self._client_class(channel)
            method_to_call = getattr(client, self._method_name)
            return method_to_call.__call__(request)


def patch_unimplemented_to_pass_through_methods(cl, opi_service_address):
    parent_class = cl.__class__.__bases__[0]
    client_class_name = parent_class.__name__.replace("Servicer", "Stub")
    client_class = getattr(import_module(parent_class.__module__), client_class_name)

    for method_name in inspect.getmembers(cl, predicate=inspect.ismethod):
        if "ServiceServicer" in str(method_name):
            logging.info(f"Patching {method_name} with pass through functor")
            setattr(
                cl,
                method_name[0],
                PassThroughGrpcCallFunctor(
                    method_name[0], opi_service_address, client_class
                ),
            )


class FrontendNvmePcie(frontend_nvme_pcie_pb2_grpc.FrontendNvmeServiceServicer):
    def __init__(self, opi_service_address):
        patch_unimplemented_to_pass_through_methods(self, opi_service_address)


class FrontendVirtioBlk(frontend_virtio_blk_pb2_grpc.FrontendVirtioBlkServiceServicer):
    def __init__(
        self, opi_service_address, qmp_address, controller_sock_dir, pci_buses
    ):
        self._opi_service_address = opi_service_address
        self._qmp_address = qmp_address
        self._controller_sock_dir = controller_sock_dir
        self._pci_buses = pci_buses
        patch_unimplemented_to_pass_through_methods(self, opi_service_address)

    def CreateVirtioBlk(self, request, context):
        response = None
        with grpc.insecure_channel(self._opi_service_address) as channel:
            client = frontend_virtio_blk_pb2_grpc.FrontendVirtioBlkServiceStub(channel)
            response = client.CreateVirtioBlk(request)

        ctrlr = str(request.virtio_blk.id.value)
        phid = int(request.virtio_blk.pcie_id.physical_function)
        print(f"### {ctrlr} - {phid} - {response}")
        with qmp.QMPClient(self._qmp_address) as qmp_client:
            qmp_client.chardev_add(
                {
                    "id": ctrlr,
                    "backend": {
                        "type": "socket",
                        "data": {
                            "addr": {
                                "type": "unix",
                                "data": {
                                    "path": os.path.join(
                                        self._controller_sock_dir, ctrlr
                                    ),
                                },
                            },
                            "server": False,
                        },
                    },
                }
            )

            for bus in self._pci_buses:
                if phid >= bus.get("count"):
                    phid = phid - bus.get("count")
                else:
                    break
            else:
                pass

            qmp_client.device_add(
                {
                    "driver": "vhost-user-blk-pci",
                    "chardev": ctrlr,
                    "bus": bus.get("name"),
                    "addr": hex(phid),
                    "id": ctrlr,
                }
            )
        return response

    def DeleteVirtioBlk(self, request, context):
        ctrlr = str(request.name)
        try:
            with qmp.QMPClient(self._qmp_address) as qclient:
                qclient.device_del(
                    {"id": ctrlr},
                    {"event": "DEVICE_DELETED", "data": {"device": ctrlr}},
                )
        except qmp.QMPError:
            logging.error("QMP: Failed to delete device")

        try:
            with qmp.QMPClient(self._qmp_address) as qclient:
                qclient.chardev_remove({"id": ctrlr})
        except qmp.QMPError:
            logging.error("QMP: Failed to delete chardev")

        with grpc.insecure_channel(self._opi_service_address) as channel:
            client = frontend_virtio_blk_pb2_grpc.FrontendVirtioBlkServiceStub(channel)
            return client.DeleteVirtioBlk(request)


class BackendNvmeTcp(backend_nvme_tcp_pb2_grpc.NVMfRemoteControllerServiceServicer):
    def __init__(self, opi_service_address):
        patch_unimplemented_to_pass_through_methods(self, opi_service_address)


def serve():
    proxy_port = "50053"
    opi_server_port = 50052
    opi_service_address = f"localhost:{opi_server_port}"
    qmp_address = ("0.0.0.0", 5555)
    controller_sock_dir = "/home/akoltun/misc/ipdk_test"
    pci_buses = [
        {"name": "pci.ipdk.0", "count": 32},
        {"name": "pci.ipdk.1", "count": 32},
    ]

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    frontend_virtio_blk_pb2_grpc.add_FrontendVirtioBlkServiceServicer_to_server(
        FrontendVirtioBlk(
            opi_service_address, qmp_address, controller_sock_dir, pci_buses
        ),
        server,
    )
    frontend_nvme_pcie_pb2_grpc.add_FrontendNvmeServiceServicer_to_server(
        FrontendNvmePcie(opi_service_address), server
    )
    backend_nvme_tcp_pb2_grpc.add_NVMfRemoteControllerServiceServicer_to_server(
        BackendNvmeTcp(opi_service_address), server
    )
    service_names = (
        frontend_virtio_blk_pb2.DESCRIPTOR.services_by_name[
            "FrontendVirtioBlkService"
        ].full_name,
        frontend_nvme_pcie_pb2.DESCRIPTOR.services_by_name[
            "FrontendNvmeService"
        ].full_name,
        backend_nvme_tcp_pb2.DESCRIPTOR.services_by_name[
            "NVMfRemoteControllerService"
        ].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)
    server.add_insecure_port("[::]:" + proxy_port)
    server.start()
    print("Server started, listening on " + proxy_port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
