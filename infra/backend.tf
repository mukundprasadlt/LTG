terraform {
    backend "azurerm" {
        resource_group_name  = var.bkstrgrg
        storage_account_name = var.bkstrg
        container_name       = var.bkcontainer
        key                  = var.bkstrgkey
    }
}