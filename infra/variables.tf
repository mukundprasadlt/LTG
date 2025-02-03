variable "prefix" {
  type        = string
  default     = "ltgenius"
  description = "A prefix used for all resources in this example"
}

variable "location" {
  type        = string
  description = "The Azure Region in which all resources should be provisioned"
}

variable "resource_group_name" {
  type        = string
  description = "RG name in Azure"
}

variable "cluster_name" {
  type        = string
  description = "AKS name in Azure"
}

variable "kubernetes_version" {
  type        = string
  description = "Kubernetes version"
}

variable "tags" {
  type        = map(string)
  default     = null
  description = "(Optional) Tags of the resource."
}

variable "bkstrgrg" {
  type        = string
  description = "The name of the backend storage account resource group"
}

variable "bkstrg" {
  type        = string
  description = "The name of the backend storage account"
}

variable "bkcontainer" {
  type = string
  description = "The container name for the backend config"
}

variable "bkstrgkey" {
  type = string
  description = "The access key for the storage account"
  default = "<storage account key>"
}