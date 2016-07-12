FROM pritunl/archlinux
MAINTAINER Julien BONACHERA <julien@bonachera.fr>

ENTRYPOINT /sbin/entrypoint
EXPOSE 53/udp
EXPOSE 53/tcp

RUN pacman -S --noconfirm git make gcc autoconf automake gnutls libcap-ng liburcu zlib lmdb jansson pkg-config libedit && \
    git clone --depth 1 https://gitlab.labs.nic.cz/labs/knot.git /usr/local/src/knot && \
    cd /usr/local/src/knot && \
    autoreconf -i -f && \
    ./configure --prefix=/usr --sbindir /usr/bin --sysconfdir=/etc --localstatedir=/var/lib \
    --libexecdir=/usr/lib/knot  --with-rundir=/run/knot --with-storage=/var/lib/knot \
    --enable-recvmmsg=yes --disable-silent-rules && \
    make && \
    make install && \
    ldconfig && \
    pacman -R --noconfirm  git make gcc autoconf automake pkg-config && \
    rm -rf /usr/local/src/knot && \
    useradd -r knot && \
    chown -R knot:knot /run/knot /var/lib/knot
VOLUME /var/lib/knot/
ADD knot.conf /etc/knot/knot.conf
ADD entrypoint /sbin/entrypoint
ADD zones /etc/knot/zones
