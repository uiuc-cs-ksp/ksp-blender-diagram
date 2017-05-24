FROM amlinux/blender-python

RUN apt-get update && apt-get install -y git

RUN cd /root && git clone https://github.com/taniwha/io_object_mu.git && git clone https://github.com/Dasoccerguy/io_kspblender.git

CMD /bin/bash -H
