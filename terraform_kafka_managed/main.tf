terraform {
    required_providers {
        yandex = {
            source = "yandex-cloud/yandex"
        }
    }
    required_version = ">= 0.13"
}

provider "yandex" {
    zone = "ru-central1-a" # Это есть в data, но такое не делают в блоках provider {} или backend {}
}

module "kafka_cluster" {
    source = "git@github.com:terraform-yacloud-modules/terraform-yandex-mdb-kafka.git"

    assign_public_ip = true
    network_id = var.network_id
    subnet_ids = var.subnet_ids
    zones = [data.yandex_client_config.client.zone]

    kafka_version = "3.5"
    cluster_name = var.cluster_name

    kafka_resource_preset_id = var.kafka_resource_preset_id
    kafka_disk_size = var.kafka_disk_size
    kafka_disk_type_id = "network-ssd"

    brokers_count = var.brokers_count

    maintenance_window_type = "ANYTIME"
    zookeeper_resource_preset_id = var.zookeeper_resource_preset_id
    zookeeper_disk_type_id = "network-ssd"
    zookeeper_disk_size = var.zookeeper_disk_size

    schema_registry = true
}