@description('Name of the project or solution')
@minLength(3)
@maxLength(22)
param projectName string

@description('Deployment Location')
@allowed([
  'centralus'
  'southcentralus'
])
param location string = 'centralus'


@allowed([
  'Standard_LRS'
  'Standard_GRS'
  'Standard_RAGRS'
  'Standard_ZRS'
  'Premium_LRS'
  'Premium_ZRS'
  'Standard_GZRS'
  'Standard_RAGZRS'
])
param stSKU string = 'Standard_LRS'

@description('Resource tags')
param resourceTags object = {
  environment: 'test'
}

// setup storage account name
var storageAccountName = toLower('st${projectName}')

resource st 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: stSKU
  }
  kind: 'StorageV2'
   properties: {
     accessTier: 'Hot'
   }
  tags: resourceTags
}

output storageAccountId string = st.id
output storageAccountName string = st.name
