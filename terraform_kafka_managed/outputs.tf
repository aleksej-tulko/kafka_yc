output "kafka_id" {
  description = "ID кластера в облаке"
  value = module.kafka_cluster.kafka_cluster_id
}

output "kafka_hosts" {
  description = "FQDN хостов"
  value = module.kafka_cluster.hosts
}

output "kafka_topics" {
  description = "Созданные топики"
  value = module.kafka_cluster.kafka_topic_ids
}

output "kafka_users" {
  description = "Пользователи Kafka"
  value = module.kafka_cluster.kafka_user_ids
}
