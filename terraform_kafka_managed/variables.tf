variable "kafka_version" {
  description = "Версия Kafka"
  type        = string
}

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
  description = "Размер диска для Zookeeper"
  type        = number
}

variable "network_id" {
  description = "ID сети, в которой будет создан кластер"
  type        = string
}

variable "subnet_ids" {
  description = "Список ID подсетей для размещения брокеров Kafka"
  type        = list(string)
}

variable "kafka_topics" {
  description = "Настройки брокеров и топиков"
  type = list(object({
    name               = string
    partitions         = number
    replication_factor = number
    config = object({
      cleanup_policy        = string
      compression_type      = string
      delete_retention_ms   = number
      file_delete_delay_ms  = number
      flush_messages        = number
      flush_ms              = number
      min_compaction_lag_ms = number
      retention_bytes       = number
      retention_ms          = number
      max_message_bytes     = number
      min_insync_replicas   = number
      segment_bytes         = number
      preallocate           = bool
    })
  }))
  default = [{
    name               = ""
    partitions         = 1
    replication_factor = 1
    config = {
      cleanup_policy        = ""
      compression_type      = ""
      delete_retention_ms   = 1
      file_delete_delay_ms  = 1
      flush_messages        = 1
      flush_ms              = 1
      min_compaction_lag_ms = 1
      retention_bytes       = 1
      retention_ms          = 1
      max_message_bytes     = 1
      min_insync_replicas   = 1
      segment_bytes         = 1
      preallocate           = false
    }
  }]
}

variable "kafka_users" {
  description = "Пользователи Kafka"
  type = list(object({
    name     = string
    password = string
    permissions = list(object({
      topic_name  = string
      role        = string
      allow_hosts = list(string)
    }))
  }))
  default = [{
    name = ""
    password = ""
    permissions = [{
      topic_name = ""
      role = ""
      allow_hosts = [""]
    }]
  }]
}