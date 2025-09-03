variable "brokers_count" {
  description = "Количество брокеров в Kafka-кластере"
  type        = number
}

variable "cluster_name" {
  description = "Имя Kafka-кластера"
  type        = string
}

variable "kafka_resource_preset_id" {
  description = "Пресет ресурсов для брокеров Kafka"
  type        = string
}

variable "kafka_disk_size" {
  description = "Размер диска для каждого брокера Kafka"
  type        = number
}

variable "zookeeper_resource_preset_id" {
  description = "Пресет ресурсов для Zookeeper"
  type        = string
}

variable "zookeeper_disk_size" {
  description = "Размер диска (в ГБ) для Zookeeper"
  type        = number
}

variable "network_id" {
  description = "ID сети , в которой будет создан кластер"
  type        = string
}

variable "subnet_ids" {
  description = "Список ID подсетей для размещения брокеров Kafka"
  type        = list(string)
}
