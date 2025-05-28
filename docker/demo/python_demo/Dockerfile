FROM ubuntu:22.04 AS builder

ENV TZ=Asia/Shanghai

COPY {Python-x.x.x.tgz} /tmp/python3.tgz

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && && chmod 1777 /tmp \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
        libnss3-dev libssl-dev libreadline-dev libffi-dev \
        ca-certificates \
    && mkdir /usr/local/python3 \
    && tar -xf /tmp/python3.tgz -C /usr/local/python3 --strip-components=1 \
    && cd /usr/local/python3 \
    && ./configure --enable-optimizations \
    && make -j$(nproc) && make altinstall \
    && make clean \
    && rm -rf /tmp/python3.tgz


# build python3 image
FROM ubuntu:22.04

ENV TZ=Asia/Shanghai

# /usr/local/bin: 2to3-3.9  idle3.9  pip3.9  pydoc3.9  python3.9  python3.9-config
# /usr/local/lib: libpython3.9.a  pkgconfig  python3.9

COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/lib /usr/local/lib

RUN apt-get update && apt-get install -y --no-install-recommends \
        libssl3 libncurses6 libreadline8 zlib1g libffi8 libgdbm6 libnss3 \
    && apt-get install tzdata -y --no-install-recommends \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && ln -sf /usr/local/bin/python3.9 /usr/bin/python3 \
    && ln -sf /usr/local/bin/pip3.9 /usr/bin/pip3 \
    && ln -sf /usr/local/bin/python3.9 /usr/bin/python \
    && ln -sf /usr/local/bin/pip3.9 /usr/bin/pip \
    && mkdir -p /root/.pip && echo "[global]\n\
index-url = https://mirrors.aliyun.com/pypi/simple/\n\
extra-index-url = https://pypi.tuna.tsinghua.edu.cn/simple/\n\
    https://pypi.doubanio.com/simple/\n\
    https://mirrors.cloud.tencent.com/pypi/simple/\n\
trusted-host = mirrors.aliyun.com\n\
    pypi.tuna.tsinghua.edu.cn\n\
    pypi.doubanio.com\n\
    mirrors.cloud.tencent.com" > /root/.pip/pip.conf \
    && apt-get install -y vim --no-install-recommends \
    && apt-get install -y curl --no-install-recommends \
    && apt-get install -y supervisor --no-install-recommends && mkdir -p /etc/supervisor/conf.d \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*







# FROM ubuntu:22.04

# ENV TZ=Asia/Shanghai

# # python download: https://www.python.org/ftp/python/
# # docker run -it --rm -v /data/lwq/software/Python-3.9.21.tgz:/tmp/python3.tgz  ubuntu:22.04 bash
# COPY Python-3.9.21.tgz /tmp/python3.tgz
# # COPY python3.tgz /tmp/python3.tgz

# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
#     && apt-get update \
#     && apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
#         libnss3-dev libssl-dev libreadline-dev libffi-dev --no-install-recommends \
#     && mkdir /usr/local/python3 \
#     && tar -xf /tmp/python3.tgz -C /usr/local/python3 --strip-components=1 \
#     && rm -rf /tmp/python3.tgz \
#     && cd /usr/local/python3 \
#     && sh ./configure --enable-optimizations \
#     && make && make altinstall \
#     && make clean \
#     && cd / && rm -rf /usr/local/python3 \
#     && ln -sf /usr/local/bin/python3.9 /usr/bin/python3 \
#     && ln -sf /usr/local/bin/pip3.9 /usr/bin/pip3 \
#     && ln -sf /usr/local/bin/python3.9 /usr/bin/python \
#     && ln -sf /usr/local/bin/pip3.9 /usr/bin/pip \
#     && apt-get remove --purge -y build-essential \
#     && apt-get autoremove -y \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*





