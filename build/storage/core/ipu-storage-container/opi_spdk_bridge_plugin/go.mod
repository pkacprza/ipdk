module ipdk_kvm_plugin

go 1.19

replace opi.storage.v1 => ../../../opi-spdk-bridge/server

require (
	github.com/digitalocean/go-qemu v0.0.0-20221209210016-f035778c97f7
	github.com/opiproject/opi-api v0.0.0-20221220003855-844775ae0e14
	github.com/ulule/deepcopier v0.0.0-20200430083143-45decc6639b6
	google.golang.org/protobuf v1.28.1
	opi.storage.v1 v0.0.1
)

require (
	github.com/digitalocean/go-libvirt v0.0.0-20220804181439-8648fbde413e // indirect
	github.com/golang/protobuf v1.5.2 // indirect
	golang.org/x/net v0.4.0 // indirect
	golang.org/x/sys v0.3.0 // indirect
	golang.org/x/text v0.5.0 // indirect
	google.golang.org/genproto v0.0.0-20221206210731-b1a01be3a5f6 // indirect
	google.golang.org/grpc v1.51.0 // indirect
)
