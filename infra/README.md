<!-- BEGIN_TF_DOCS -->

# terraform-azurerm-ltgenius

### Overview

This is the Terraform AKS deployment for LTGenius

## Deployment Steps

1. Configure Service connection with appropiate permissions. Contributor and Rloe assignment for the whole subscription.
2. Create Storage account and container for the tfstate. See backend.tf
3. The RG used to deploy the AKS cluster must be created manuially and used under the file data.tf
4. Run the azure deployment pipeline.

<!-- markdownlint-disable MD033 -->

## Requirements

The following requirements are needed by this module:

- <a name="requirement_terraform"></a> [terraform](#requirement_terraform) (>= 1.3.0)

- <a name="requirement_azurerm"></a> [azurerm](#requirement_azurerm) (>=4.0)

<!-- markdownlint-disable MD013 -->

## Required Inputs

The following input variables are required:

### <a name="location"></a> [location](#input_location)

### <a name="resource_group_name"></a> [resource_group_name](#input_resource_group_name)

### <a name="cluster_name"></a> [cluster_name](#input_cluster_name)

### <a name="kubernetes_version"></a> [kubernetes_version](#input_kubernetes_version)

### <a name="bkstrgrg"></a> [bkstrgrg](#input_bkstrgrg)

### <a name="bkstrg"></a> [bkstrg](#input_bkstrg)

### <a name="bkcontainer"></a> [bkcontainer](#input_bkcontainer)

### <a name="bkstrgkey"></a> [bkstrgkey](#input_bkstrgkey)

## Optional Inputs

The following input variables are optional (have default values):

### <a name="prefix"></a> [prefix](#input_prefix)

### <a name="tags"></a> [tags](#input_tags)
