FROM amlinux/blender-python

RUN apt-get update && apt-get install -y vim less python3-pip python3-numpy git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN cd /root && \
    git clone https://github.com/galvanized/io_kspblender.git && \
    git clone https://github.com/taniwha/io_object_mu.git && \
    git clone https://github.com/taniwha/cfgnode.git && \
    git clone https://github.com/uiuc-cs-ksp/ksp-blender-diagram.git && \
    echo "/data/v1.2.2_multi" > io_kspblender/kspdir.txt

CMD /bin/bash -H
