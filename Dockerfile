ARG python_version
FROM python:${python_version}-slim

ARG nodejs_major_version=14
ARG nodejs_minor_version=3
ARG nodejs_revision=0
ARG mountebank_version=2.2.1
ARG nodejs_apt_version=$nodejs_major_version.$nodejs_minor_version.${nodejs_revision}-1nodesource1

RUN apt-get update && apt-get -y install curl --no-install-recommends \
    && curl -sL https://deb.nodesource.com/setup_$nodejs_major_version.x | bash - \
    && apt-get -y install nodejs=$nodejs_apt_version --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# We choose the user and group ID to match the TravisCI executor user and group, to avoid permission issues
# when writing to bind-mounted folders.
ARG user_id=1001
ARG group_id=1002
ARG user=travisci
ARG group=travisci
RUN addgroup --system $group --gid $group_id && adduser $user --gid $group_id --uid $user_id
ARG workdir=/mbtest
RUN mkdir -p $workdir && chown $user:$group $workdir
USER $user
ENV PATH /home/$user/.local/bin:/home/$user/bin:$PATH
ENV PYTHONPATH=${PYTHONPATH}:$workdir;${PYTHONPATH}:$workdir/src
WORKDIR $workdir
RUN npm install mountebank@$mountebank_version --production
COPY --chown=${user}:${group} . ./
RUN pip install -e .[test,coverage,docs] --user
