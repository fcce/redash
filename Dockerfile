FROM node:10 as frontend-builder

WORKDIR /frontend
COPY package.json package-lock.json /frontend/
RUN npm config set registry https://registry.npm.taobao.org
RUN npm install

COPY . /frontend
RUN npm run build

FROM redash/base:latest

# Controls whether to install extra dependencies needed for all data sources.
ARG skip_ds_deps

# We first copy only the requirements file, to avoid rebuilding on every file
# change.
COPY requirements.txt requirements_dev.txt requirements_all_ds.txt ./
RUN pip install -r requirements.txt -r requirements_dev.txt --index-url http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

RUN if [ "x$skip_ds_deps" = "x" ] ; then pip install -r requirements_all_ds.txt --index-url http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com ; else echo "Skipping pip install -r requirements_all_ds.txt" ; fi

RUN ip -4 route list match 0/0 | awk '{print $3 "host.docker.internal"}' >> /etc/hosts

COPY . /app
COPY --from=frontend-builder /frontend/client/dist /app/client/dist

ENTRYPOINT ["/app/bin/docker-entrypoint"]
CMD ["server"]
