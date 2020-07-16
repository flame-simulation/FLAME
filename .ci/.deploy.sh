#!/usr/bin/env bash

setup_git() {
    git config --global user.name "Travis CI"
}

add_files() {
    cp -arv wheelhouse/* . \
        | awk -F'->' '{print $2}' \
        | sed "s/[\'\’\ \‘]//g" > /tmp/filelist

    for ifile in `cat /tmp/filelist`
    do
        git add ${ifile}
    done
}

commit_files() {
    git stash
    git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
    git fetch
    git ls-remote | grep -i "refs/heads/dist"
    if [ $? -ne 0 ]; then
        git checkout --orphan dist
        git rm -rf .
    else
        git checkout -b dist origin/dist
    fi
    add_files
    git commit -m "Update dists by Travis build: $TRAVIS_BUILD_NUMBER"
}

push_files() {
    git remote add dist https://${FLAME_DEPLOY}@github.com/archman/flame.git
    git push --quiet --set-upstream dist dist
}

setup_git
commit_files
push_files
