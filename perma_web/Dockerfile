FROM registry.lil.tools/library/python:3.11-bookworm
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_SRC=/usr/local/src \
    OPENSSL_CONF=/etc/ssl
RUN mkdir -p /perma/perma_web
WORKDIR /perma/perma_web

# For fonts-roboto and ttf-mscorefonts-installer
RUN echo "deb http://deb.debian.org/debian bookworm main contrib" > /etc/apt/sources.list \
    && echo "deb https://deb.debian.org/debian-security bookworm-security main contrib" >> /etc/apt/sources.list \
    && echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections

# Get build dependencies and packages required by the app
RUN apt-get update \
    && apt-get install -y \
        wget \
        curl \
        bzip2 \
        gnupg \
        python3-pip \
        python3-dev \
        python-is-python3 \
        virtualenv \
        git \
        nano \
        procps `# ps and pkill` \
        \
        postgresql-client \
        libpq-dev \
        libffi-dev \
        libnss3-tools                           `# for certutil` \
        libxml2-dev \
        libxslt-dev

# node.js 
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs=20.13.0-1nodesource1

#
# npm
#

# frontend requirements
COPY perma_web/package.json /perma/perma_web
COPY perma_web/npm-shrinkwrap.json /perma/perma_web
RUN npm install \
    && rm package.json \
    && rm npm-shrinkwrap.json

# worker requirements
COPY services/js-wacz/package.json /perma/services/js-wacz/package.json
COPY services/js-wacz/package-lock.json /perma/services/js-wacz/package-lock.json
RUN npm install --prefix /perma/services/js-wacz/ \
    && rm /perma/services/js-wacz/package.json \
    && rm /perma/services/js-wacz/package-lock.json

# python requirements
COPY perma_web/requirements.txt /perma/perma_web
RUN python3 -m pip install -r /perma/perma_web/requirements.txt \
    && rm /perma/perma_web/requirements.txt

# Install Playwright browsers for integration tests
RUN  apt-get update && apt install -y --no-install-recommends libdbus-glib-1-2 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libatspi2.0-0 \
    libwayland-client0 \
    libpango-1.0-0 \
    libcairo2 \
    libx11-xcb1 \
    libxcursor1 \
    libgtk-3-0 \
    libpangocairo-1.0-0 \
    libcairo-gobject2 \
    libgdk-pixbuf-2.0-0

RUN mkdir -p $HOME/.pki/nssdb \
    && certutil -d $HOME/.pki/nssdb -N --empty-password \
    && playwright install chromium firefox
