// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2022 Intel Corporation

package main

import (
	"context"
	"fmt"
	"log"
	"strings"
	"time"

	qmp "github.com/digitalocean/go-qemu/qmp"
	qmpraw "github.com/digitalocean/go-qemu/qmp/raw"
)

const (
	qmpTcp = "tcp"
)

type QemuMonitor interface {
	AddDevice(chardev string, bus string, addr int32) error
	DeleteDevice(ctrlr string) error
	AddChardev(ctrlr string, sockPath string) error
	DeleteChardev(ctrlr string) error
}

func NewQemuMonitor(qmpConnectionProtocol string, qmpAddress string,
	timeoutSec time.Duration) (*qmpQemuMonitor, error) {
	qmpConnectionProtocol = strings.ToLower(qmpConnectionProtocol)
	if qmpConnectionProtocol != qmpTcp {
		return nil, fmt.Errorf("Not supported communication protocol: %v", qmpConnectionProtocol)
	}
	return &qmpQemuMonitor{qmpConnectionProtocol, qmpAddress, timeoutSec}, nil
}

type qmpQemuMonitor struct {
	qmpConnectionProtocol string
	qmpAddress            string

	timeoutSec time.Duration
}

func (s *qmpQemuMonitor) DeleteChardev(ctrlr string) error {
	monitor, rawMonitor, err := s.createConnectedMonitors()
	if err != nil {
		return err
	}
	defer monitor.Disconnect()

	return rawMonitor.ChardevRemove(ctrlr)
}

func (s *qmpQemuMonitor) AddDevice(chardev string, bus string, addr int32) error {
	monitor, err := s.createConnectedMonitor()
	if err != nil {
		return err
	}
	defer monitor.Disconnect()

	// Use raw json since provided in lib class do not support addr/chardev fields
	qmpCmd := fmt.Sprintf(`{
		"execute": "device_add",
		"arguments": {
			"driver": "vhost-user-blk-pci",
			"chardev": "%s",
			"bus": "%s",
			"addr": "%#x",
			"id": "%s"
		}
	}`, chardev, bus, addr, chardev)
	log.Println("QMP command to send: ", qmpCmd)
	raw, err := monitor.Run([]byte(qmpCmd))
	if err != nil {
		log.Println("QMP error:", err)
		return fmt.Errorf("Couldn't run QMP command: %v", err)
	}

	response := string(raw[:])
	log.Println("QMP response:", response)
	if strings.Contains(response, "error") {
		return fmt.Errorf(response)
	}

	return nil
}

func (s *qmpQemuMonitor) DeleteDevice(ctrlr string) error {
	monitor, rawMonitor, err := s.createConnectedMonitors()
	if err != nil {
		return err
	}
	defer monitor.Disconnect()

	err = rawMonitor.DeviceDel(ctrlr)
	if err != nil {
		return fmt.Errorf("Couldn't delete device: %v", err)
	}
	return s.waitForEvent("DEVICE_DELETED", ctrlr, monitor)
}

func (s *qmpQemuMonitor) AddChardev(ctrlr string, sockPath string) error {
	monitor, rawMonitor, err := s.createConnectedMonitors()
	if err != nil {
		return err
	}
	defer monitor.Disconnect()

	server := false
	socketBackend := qmpraw.ChardevBackendSocket{Addr: qmpraw.SocketAddressLegacyUnix{sockPath}, Server: &server}
	_, err = rawMonitor.ChardevAdd(ctrlr, socketBackend)
	return err
}

func (s *qmpQemuMonitor) waitForEvent(event string, dataTag string, monitor qmp.Monitor) error {
	begin := time.Now()
	end := begin.Add(s.timeoutSec)
	stream, _ := monitor.Events(context.TODO())

	for e := range stream {
		log.Println(e.Event)
		log.Println(e.Data)
		if dataTag != "" {
			dataTagFound := false
			for _, v := range e.Data {
				value, ok := v.(string)
				if !ok {
					continue
				}

				if strings.Contains(value, dataTag) {
					dataTagFound = true
					break
				}
			}
			if !dataTagFound {
				continue
			}
		}
		if strings.Contains(e.Event, event) {
			return nil
		}

		if time.Now().After(end) {
			return fmt.Errorf("Event %v not found", event)
		}
	}
	return fmt.Errorf("Disconnect with QEMU monitor")
}

func (s *qmpQemuMonitor) createConnectedMonitor() (qmp.Monitor, error) {
	monitor, err := qmp.NewSocketMonitor(s.qmpConnectionProtocol, s.qmpAddress, 2*time.Second)
	if err != nil {
		return nil, fmt.Errorf("Couldn't create QEMU monitor: %v", err)
	}

	err = monitor.Connect()
	if err != nil {
		return nil, fmt.Errorf("Couldn't connect to QEMU QMP monitor: %v", err)
	}

	return monitor, nil
}

func (s *qmpQemuMonitor) createConnectedMonitors() (qmp.Monitor, *qmpraw.Monitor, error) {
	monitor, err := s.createConnectedMonitor()
	if err != nil {
		return nil, nil, err
	}

	rawMonitor := qmpraw.NewMonitor(monitor)

	return monitor, rawMonitor, nil
}
