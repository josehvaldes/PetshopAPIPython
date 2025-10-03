@description('Name of the VM')
param vmName string = 'milvus-vm'

@description('Admin username for the VM')
param adminUsername string = 'azureuser'

@description('Admin password (or SSH key if preferred)')
@secure()
param adminPassword string

@description('Location for deployment')
param location string = resourceGroup().location

@description('VM size (B2s is cheap)')
param vmSize string = 'Standard_B2s'

@description('Ubuntu image')
param ubuntuImage string = '20_04-lts'

@description('Extra data disk size in GB')
param dataDiskSizeGb int = 50

var vnetName = '${vmName}-vnet'
var subnetName = 'default'
var nicName = '${vmName}-nic'
var publicIpName = '${vmName}-pip'
var nsgName = '${vmName}-nsg'
var dataDiskName = '${vmName}-datadisk'

resource vnet 'Microsoft.Network/virtualNetworks@2023-04-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
    subnets: [
      {
        name: subnetName
        properties: {
          addressPrefix: '10.0.0.0/24'
          networkSecurityGroup: {
            id: nsg.id
          }
        }
      }
    ]
  }
}

resource nsg 'Microsoft.Network/networkSecurityGroups@2023-04-01' = {
  name: nsgName
  location: location
  properties: {
    securityRules: [
      {
        name: 'SSH'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '22'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 1000
          direction: 'Inbound'
        }
      }
      {
        name: 'MilvusGrpc'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '19530'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 1001
          direction: 'Inbound'
        }
      }
      {
        name: 'MilvusRest'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '9091'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 1002
          direction: 'Inbound'
        }
      }
    ]
  }
}

resource publicIp 'Microsoft.Network/publicIPAddresses@2023-04-01' = {
  name: publicIpName
  location: location
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}

resource nic 'Microsoft.Network/networkInterfaces@2023-04-01' = {
  name: nicName
  location: location
  properties: {
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          subnet: {
            id: vnet.properties.subnets[0].id
          }
          privateIPAllocationMethod: 'Dynamic'
          publicIPAddress: {
            id: publicIp.id
          }
        }
      }
    ]
  }
}

resource dataDisk 'Microsoft.Compute/disks@2023-10-02' = {
  name: dataDiskName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    diskSizeGB: dataDiskSizeGb
    creationData: {
      createOption: 'Empty'
    }
  }
}

resource vm 'Microsoft.Compute/virtualMachines@2023-03-01' = {
  name: vmName
  location: location
  properties: {
    hardwareProfile: {
      vmSize: vmSize
    }
    osProfile: {
      computerName: vmName
      adminUsername: adminUsername
      adminPassword: adminPassword
      linuxConfiguration: {
        disablePasswordAuthentication: false
      }
      customData: base64('''
#cloud-config
package_upgrade: true
packages:
  - docker.io
  - docker-compose
runcmd:
  # prepare data disk
  - [ sh, -c, "mkfs.ext4 /dev/disk/azure/scsi1/lun0" ]
  - [ sh, -c, "mkdir -p /mnt/data" ]
  - [ sh, -c, "mount /dev/disk/azure/scsi1/lun0 /mnt/data" ]
  - [ sh, -c, "echo '/dev/disk/azure/scsi1/lun0 /mnt/data ext4 defaults,nofail 0 2' >> /etc/fstab" ]
  # docker user
  - [ sh, -c, "usermod -aG docker ${adminUsername}" ]
  # get Milvus compose
  - [ sh, -c, "curl -L https://github.com/milvus-io/milvus/releases/download/v2.6.2/milvus-standalone-docker-compose.yml -o /mnt/data/docker-compose.yml" ]
  # adjust volumes to point to /mnt/data/milvus
  - [ sh, -c, "sed -i 's#\${DOCKER_VOLUME_DIRECTORY:-.}/volumes/milvus#\/mnt/data/milvus#g' /mnt/data/docker-compose.yml" ]
  # run Milvus
  - [ sh, -c, "cd /mnt/data && docker-compose up -d" ]
      ''')
    }
    storageProfile: {
      imageReference: {
        publisher: 'Canonical'
        offer: '0001-com-ubuntu-server-focal'
        sku: ubuntuImage
        version: 'latest'
      }
      osDisk: {
        createOption: 'FromImage'
        managedDisk: {
          storageAccountType: 'Standard_LRS'
        }
      }
      dataDisks: [
        {
          lun: 0
          name: dataDisk.name
          createOption: 'Attach'
          managedDisk: {
            id: dataDisk.id
          }
          diskSizeGB: dataDiskSizeGb
        }
      ]
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: nic.id
        }
      ]
    }
  }
}

output publicIpAddress string = publicIp.properties.ipAddress
