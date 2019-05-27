./bin/spark-submit --class org.apache.spark.examples.SparkPi \
--conf "spark.driver.extraClassPath=/usr/hdp/current/spark2-client/metrocs-jars/metrics-core-3.1.2.jar:/usr/hdp/current/spark2-client/metrocs-jars/simpleclient-0.3.0.jar:/usr/hdp/current/spark2-client/metrocs-jars/simpleclient_dropwizard-0.3.0.jar:/usr/hdp/current/spark2-client/metrocs-jars/simpleclient_pushgateway-0.3.0.jar:/usr/hdp/current/spark2-client/metrocs-jars/spark-metrics_2.11-2.3-2.0.4.jar:/usr/hdp/current/spark2-client/metrocs-jars/collector-0.3.0.jar:/usr/hdp/current/spark2-client/metrocs-jars/snakeyaml-1.23.jar"    \
--conf "spark.executor.extraClassPath=/usr/hdp/current/spark2-client/metrocs-jars/metrics-core-3.1.2.jar:/usr/hdp/current/spark2-client/metrocs-jars/simpleclient-0.3.0.jar:/usr/hdp/current/spark2-client/metrocs-jars/simpleclient_dropwizard-0.3.0.jar:/usr/hdp/current/spark2-client/metrocs-jars/simpleclient_pushgateway-0.3.0.jar:/usr/hdp/current/spark2-client/metrocs-jars/spark-metrics_2.11-2.3-2.0.4.jar:/usr/hdp/current/spark2-client/metrocs-jars/collector-0.3.0.jar:/usr/hdp/current/spark2-client/metrocs-jars/snakeyaml-1.23.jar"    \
--master yarn-client     \
--num-executors 1     \
--driver-memory 512m  \
--conf spark.metrics.conf=/var/lib/spark2-metrics/spark-metrics.properties    \
--executor-memory 512m     --executor-cores 1     examples/jars/spark-examples*.jar 10
