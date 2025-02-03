resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
  tags = var.tags
}

resource "azurerm_virtual_network" "avnet" {
  name                = "${var.prefix}-network"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  address_space       = ["10.1.0.0/16"]
}

resource "azurerm_subnet" "asubnet" {
  name                 = "internal"
  virtual_network_name = azurerm_virtual_network.avnet.name
  resource_group_name  = azurerm_resource_group.rg.name
  address_prefixes     = ["10.1.0.0/22"]
}

resource "azurerm_container_registry" "acr" {
  location            = azurerm_resource_group.rg.location
  name                = "cregltgenius"
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Premium"
  tags                = var.tags
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.cluster_name
  kubernetes_version  = var.kubernetes_version
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = var.cluster_name

  default_node_pool {
    name                = "system"
    vm_size             = "Standard_DS2_v2"
    type                = "VirtualMachineScaleSets"
    auto_scaling_enabled  = true
    node_count            = 1
    max_count             = 3
    min_count             = 1
    vnet_subnet_id = azurerm_subnet.asubnet.id
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    load_balancer_sku = "standard"
    network_plugin    = "kubenet" # azure (CNI)
  }

  tags = var.tags

}

resource "azurerm_kubernetes_cluster_node_pool" "workers" {
  name                  = "workers"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks.id
  vm_size               = "Standard_DS2_v2"
  vnet_subnet_id = azurerm_subnet.asubnet.id
  auto_scaling_enabled  = true
  node_count            = 1
  max_count             = 5
  min_count             = 1
  os_sku                = "Ubuntu"
  mode                  = "User"
  tags = var.tags
}

resource "azurerm_role_assignment" "ara" {
  principal_id                     = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  scope                            = azurerm_container_registry.acr.id
  role_definition_name             = "AcrPull"
  skip_service_principal_aad_check = true
}