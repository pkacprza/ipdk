// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2022 Intel Corporation

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"

	pb "github.com/opiproject/opi-api/storage/v1alpha1/gen/go"
	"github.com/ulule/deepcopier"
	"google.golang.org/protobuf/types/known/emptypb"

	"opi.storage.v1/bridge"
)

type ipdkKvmWrapper struct {
	bridge.GrpcServer
	qemuMonitor QemuMonitor

	qemuPciBuses      []string
	controllerSockDir string
}

func (s *ipdkKvmWrapper) calculateBusPhid(phid int32) (bus string, newPhid int32) {
	for _, element := range s.qemuPciBuses {
		if phid >= 32 {
			phid = phid - 32
		} else {
			newPhid = phid
			bus = element
		}
	}
	return
}

func (s *ipdkKvmWrapper) CreateVirtioBlk(ctx context.Context,
	in *pb.CreateVirtioBlkRequest) (*pb.VirtioBlk, error) {
	if in.VirtioBlk.Id.Value == "" {
		in.VirtioBlk.Id.Value = fmt.Sprintf("virtio_blk-opi-%v", in.VirtioBlk.PcieId.PhysicalFunction)
	}
	response, err := s.GrpcServer.CreateVirtioBlk(ctx, in)
	if err != nil {
		log.Println("Error running underlying cmd on opi-spdk bridge:", err)
		return response, err
	}

	// TODO: modify just required members
	err = deepcopier.Copy(in.VirtioBlk).To(response)
	if err != nil {
		log.Println("Cannot set response structure:", err)
		return response, err
	}

	ctrlr := in.VirtioBlk.Id.Value
	socketPath := filepath.Join(s.controllerSockDir, ctrlr)
	err = s.qemuMonitor.AddChardev(ctrlr, socketPath)
	if err != nil {
		log.Println(err)
		deleteIn := pb.DeleteVirtioBlkRequest{}
		deleteIn.Name = response.GetId().Value
		_, err = s.GrpcServer.DeleteVirtioBlk(ctx, &deleteIn)
		return response, fmt.Errorf("Couldn't create chardev")
	}

	phid := in.VirtioBlk.PcieId.PhysicalFunction
	bus, phidOnBus := s.calculateBusPhid(phid)
	s.qemuMonitor.AddDevice(ctrlr, bus, phidOnBus)
	if err != nil {
		s.qemuMonitor.DeleteChardev(ctrlr)

		deleteIn := pb.DeleteVirtioBlkRequest{}
		deleteIn.Name = response.GetId().Value
		_, err = s.GrpcServer.DeleteVirtioBlk(ctx, &deleteIn)
		return response, fmt.Errorf("Couldn't add device")
	}

	return response, nil
}

func (s *ipdkKvmWrapper) DeleteVirtioBlk(ctx context.Context,
	in *pb.DeleteVirtioBlkRequest) (*emptypb.Empty, error) {
	ctrlr := in.Name
	err := s.qemuMonitor.DeleteDevice(ctrlr)
	if err != nil {
		return &emptypb.Empty{}, fmt.Errorf("Couldn't delete virtio-blk: %v", err)
	}

	err = s.qemuMonitor.DeleteChardev(ctrlr)
	if err != nil {
		// TODO How to handle? Device is partially destroyed
		return &emptypb.Empty{}, fmt.Errorf("Couldn't delete chardev for virtio-blk: %v", err)
	}

	response, err := s.GrpcServer.DeleteVirtioBlk(ctx, in)
	if err != nil {
		log.Println("Error running underlying cmd on opi-spdk bridge:", err)
		return response, err
	}
	return response, err
}

type opiSpdkBridgeKvmPlugin struct {
}

func (_ opiSpdkBridgeKvmPlugin) Plug(s bridge.GrpcServer, configPath string) (bridge.GrpcServer, error) {
	log.Println("Create IPDK KVM wrapper")
	configData, err := os.ReadFile(configPath)
	if err != nil {
		return nil, fmt.Errorf("Couldn't read config file: %v", err)
	}
	conf := struct {
		Plugin struct {
			QmpConnectionProtocol string   `json:"qmpConnectionProtocol"`
			QmpAddress            string   `json:"qmpAddress"`
			ControllerSockDir     string   `json:"controllerSockDir"`
			QemuPciBuses          []string `json:"qemuPciBuses"`
		} `json:"plugin"`
	}{}
	fmt.Println(string(configData[:]))
	err = json.Unmarshal(configData, &conf)
	if err != nil {
		fmt.Println(err)
		return nil, err
	}
	pluginConf := conf.Plugin
	log.Println(pluginConf)
	monitor, err := NewQemuMonitor(pluginConf.QmpConnectionProtocol, pluginConf.QmpAddress, 10*time.Second)
	if err != nil {
		return nil, err
	}

	return &ipdkKvmWrapper{s, monitor, pluginConf.QemuPciBuses, pluginConf.ControllerSockDir}, nil
}

var OpiSpdkBridgePlugin = opiSpdkBridgeKvmPlugin{}
