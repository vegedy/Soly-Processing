FROM flink:2.2.1-java17@sha256:c5124717afe3829cc2d7c9b538bfe0b9d66cae3107a174d8f0e0392abe6375b8 AS base
USER root
ENV PATH="/opt/python/bin:${PATH}" \
    LD_LIBRARY_PATH="/opt/python/lib" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYFLINK_CLIENT_EXECUTABLE=/opt/python/bin/python3 \
    PYFLINK_PYTHON=/opt/python/bin/python3
COPY docker/install-system.sh /tmp/install-system.sh
RUN bash /tmp/install-system.sh runtime

FROM base AS python-builder
RUN bash /tmp/install-system.sh build
WORKDIR /tmp/python-build
RUN curl --fail --location --retry 3 --output Python.tar.xz https://www.python.org/ftp/python/3.12.15/Python-3.12.15.tar.xz \
    && echo 'c2c4321961fab0fb999d66e0cecf521c2ab3994c7992873ea99e306c1094fd5a  Python.tar.xz' | sha256sum --check - \
    && tar -xJf Python.tar.xz --strip-components=1 \
    && ./configure --prefix=/opt/python --enable-shared --with-ensurepip=install \
    && make -j 4 \
    && make install \
    && python3 --version

FROM python-builder AS package-builder
WORKDIR /build
COPY requirements/build.txt requirements/build.txt
RUN python3 -m pip install --require-hashes --only-binary=:all: -r requirements/build.txt
COPY requirements/runtime.txt requirements/runtime.txt
# PyFlink has source-only dependencies; build with the locked backend, never isolation.
RUN python3 -m pip wheel --require-hashes --no-build-isolation --wheel-dir /wheels -r requirements/runtime.txt
COPY pyproject.toml README.md LICENSE ./
COPY src/ src/
RUN python3 -m pip wheel --no-deps --no-build-isolation --wheel-dir /wheels .
COPY connectors/pom.xml connectors/jars.lock.json connectors/fetch_jars.py connectors/
RUN python3 connectors/fetch_jars.py /connectors

FROM base AS runtime
COPY --from=python-builder /opt/python /opt/python
COPY --from=package-builder /wheels /tmp/wheels
RUN python3 -m pip install --no-index --no-deps /tmp/wheels/*.whl \
    && python3 -m pip check \
    && rm -rf /tmp/wheels /tmp/install-system.sh \
    && printf '/opt/python/lib\n' > /etc/ld.so.conf.d/soly-python.conf \
    && ldconfig
COPY --from=package-builder /connectors/ /opt/flink/lib/
COPY docker/smoke_test.py /opt/soly/smoke_test.py
# Keep the official entrypoint/CMD and its JobManager/TaskManager roles.
# Both client and worker select exactly the same Python interpreter.
RUN printf '\npython:\n  client:\n    executable: /opt/python/bin/python3\n  executable: /opt/python/bin/python3\n' >> /opt/flink/conf/config.yaml
USER flink
WORKDIR /opt/flink
