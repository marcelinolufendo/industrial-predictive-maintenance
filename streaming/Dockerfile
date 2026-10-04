FROM apache/spark:3.5.0

USER root

RUN pip install --no-cache-dir \
    pandas>=2.2.2 \
    numpy>=2.0.0 \
    scikit-learn>=1.6.0 \
    xgboost>=2.1.1 \
    mlflow>=2.15.1

COPY stream_processor.py /opt/spark/jobs/stream_processor.py

CMD ["/opt/spark/bin/spark-submit", \
     "--master", "spark://spark-master:7077", \
     "--packages", "io.delta:delta-spark_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0", \
     "--conf", "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension", \
     "--conf", "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog", \
     "--conf", "spark.executor.memory=1g", \
     "--conf", "spark.driver.memory=1g", \
     "/opt/spark/jobs/stream_processor.py"]
