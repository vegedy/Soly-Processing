"""Check the installed Python/JVM runtime and connector planning without services."""

import subprocess
import sys
import sysconfig
from importlib import import_module
from importlib.metadata import version
from pathlib import Path


def main() -> None:
    if sys.version_info[:3] != (3, 12, 15):
        raise RuntimeError(f"Expected Python 3.12.15, got {sys.version}")
    package = import_module("soly_processing")
    if package.__file__ is None:
        raise RuntimeError("Installed package has no file")
    if not Path(package.__file__).resolve().is_relative_to(
        Path(sysconfig.get_path("purelib")).resolve()
    ):
        raise RuntimeError("Package was not imported from site-packages")
    if version("apache-flink") != "2.2.1":
        raise RuntimeError("Expected PyFlink 2.2.1")
    java = subprocess.run(["java", "-version"], check=True, capture_output=True, text=True)
    print(java.stderr.strip(), flush=True)
    print(f"Python {sys.version.split()[0]}, PyFlink {version('apache-flink')}")
    print(f"soly-processing {version('soly-processing')}: {package.__file__}")

    from pyflink.common import Configuration
    from pyflink.datastream import StreamExecutionEnvironment
    from pyflink.java_gateway import get_gateway
    from pyflink.table import StreamTableEnvironment

    config = Configuration()
    config.set_string("python.client.executable", sys.executable)
    config.set_string("python.executable", sys.executable)
    env = StreamExecutionEnvironment.get_execution_environment(config)
    env.set_parallelism(1)
    table_env = StreamTableEnvironment.create(env)
    gateway = get_gateway()
    jvm = gateway.jvm
    if not jvm.java.lang.System.getProperty("java.version").startswith("17."):
        raise RuntimeError("Expected Java 17 in the PyFlink gateway")
    flink_version = jvm.org.apache.flink.runtime.util.EnvironmentInformation.getVersion()
    if flink_version != "2.2.1":
        raise RuntimeError(f"Expected Flink 2.2.1, got {flink_version}")
    loader = jvm.java.lang.Thread.currentThread().getContextClassLoader()
    for name in (
        "org.apache.flink.connector.kafka.source.KafkaSource",
        "org.apache.flink.connector.kafka.table.KafkaDynamicTableFactory",
        "org.apache.kafka.clients.consumer.KafkaConsumer",
        "org.apache.flink.connector.jdbc.core.table.JdbcDynamicTableFactory",
        "org.apache.flink.connector.jdbc.postgres.database.dialect.PostgresDialect",
        "org.postgresql.Driver",
    ):
        clazz = jvm.java.lang.Class.forName(name, True, loader)
        clazz.getDeclaredConstructors()
        clazz.getDeclaredMethods()
        print(f"Loaded {name}", flush=True)

    table_env.execute_sql("""
        CREATE TEMPORARY TABLE smoke_kafka (payload STRING) WITH (
          'connector' = 'kafka', 'topic' = 'smoke',
          'properties.bootstrap.servers' = '127.0.0.1:1',
          'properties.group.id' = 'smoke',
          'scan.startup.mode' = 'earliest-offset', 'format' = 'raw'
        )
    """)
    table_env.execute_sql("""
        CREATE TEMPORARY TABLE smoke_jdbc (id BIGINT, PRIMARY KEY (id) NOT ENFORCED)
        WITH ('connector' = 'jdbc',
              'url' = 'jdbc:postgresql://127.0.0.1:1/smoke',
              'table-name' = 'smoke', 'driver' = 'org.postgresql.Driver')
    """)
    # Planning exercises service discovery and the Postgres dialect without I/O.
    table_env.explain_sql("SELECT payload FROM smoke_kafka")
    table_env.explain_sql("INSERT INTO smoke_jdbc SELECT CAST(1 AS BIGINT)")
    print("Local PyFlink environment and Kafka/JDBC plans OK", flush=True)
    gateway.shutdown()


if __name__ == "__main__":
    main()
