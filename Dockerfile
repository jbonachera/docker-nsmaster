FROM jbonachera/arch
MAINTAINER Julien BONACHERA <julien@bonachera.fr>

ENTRYPOINT /sbin/entrypoint
HEALTHCHECK --interval=10s --timeout=3s CMD knotc status || exit 1
EXPOSE 53/udp
EXPOSE 53/tcp

RUN pacman -S --noconfirm git make gcc autoconf automake libcap-ng liburcu lmdb jansson pkg-config libedit protobuf-c libevent && \
    cd /usr/local/src/ && \
    git clone https://github.com/farsightsec/fstrm.git && \ 
    cd fstrm && ./autogen.sh && ./configure --prefix=/usr --sbindir /usr/bin --sysconfdir=/etc --localstatedir=/var/lib && \
    make && make install && cd / && rm -rf /usr/local/src/fstrm/ && \
    git clone --depth 1 https://gitlab.labs.nic.cz/labs/knot.git /usr/local/src/knot && \
    cd /usr/local/src/knot && \
    autoreconf -i -f && \
    ./configure --enable-dnstap --prefix=/usr --sbindir /usr/bin --sysconfdir=/etc --localstatedir=/var/lib \
    --libexecdir=/usr/lib/knot  --with-rundir=/run/knot --with-storage=/var/lib/knot \
    --enable-recvmmsg=yes --disable-silent-rules && \
    make && \
    make install && \
    ldconfig && \
    pacman -Rcs --noconfirm  git make gcc autoconf automake pkg-config && \
    rm -rf /usr/local/src/knot && \
    useradd -r knot && \
    chown -R knot:knot /run/knot /var/lib/knot
VOLUME /var/lib/knot/
ADD knot.conf.jinja2 /etc/knot/knot.conf.jinja2
ADD entrypoint /sbin/entrypoint
ADD zones /etc/knot/zones
