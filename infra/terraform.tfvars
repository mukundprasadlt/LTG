location            = "East US"
resource_group_name = "aks_ltgenius_rg"
cluster_name        = "ltgenius-aks"
kubernetes_version  = "1.30.3"
bkstrgrg            = "cl-CirrusAI-LTGenius"
bkstrg              = "ltgeniusterraform"
bkcontainer         = "tfstate"
bkstrgkey           = "terraform.tfstate"
tags                = {
    "Environment" = "Production"
    "Owner" = "Ayub-Carlos"
    "Project" = "LTGenius"
}