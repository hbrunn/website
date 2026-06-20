Introduction
------------

This action checks that vendored files match some specific version of a package as defined in a file called `vendor-libs.json` located in the passed directories.

In times of rampant supply chain attacks, vendored files belong to the most obvious hiding places for nefarious code, as reviewers tend to take them as a black box, and should be able to do so, which this check allows. When you have activated it, for any change to vendor files in your repository, reviewers only have to check if the defined origin is trustworthy, and leave the rest to the checker which will fail if the code provided does not match the origin.

A very welcome side effect of forcing to declare the origin of vendored code is that it simplifies updating versions, and enables checking for vulnerabilities automatically.

Howto
-----

Suppose your repository contains some vendored files in folder `/external`:

    /external/bootstrap.css
    /external/bootstrap.js
    ...

Then in `/external/vendor-libs.json`, you need to describe where each file comes from:

```json
{
    "bootstrap.css": {
        "purl": "pkg:github/twbs/bootstrap@v5.3.8#dist/css"
    },
    "bootstrap.js": {
        "purl": "pkg:github/twbs/bootstrap@v5.3.8#dist/js"
    }
}
```

This says that the mentioned files can be found on github in repository twbs/bootstrap with version v5.3.8, subfolders dist/js and dist/css respectively. When the check is run, it will compare the files in your repository with [bootstrap.css](https://github.com/twbs/bootstrap/blob/v5.3.8/dist/css/bootstrap.css) and [bootstrap.js](https://github.com/twbs/bootstrap/blob/v5.3.8/dist/js/bootstrap.js) on github, and fail if there's a difference.

The origin is expressed as [Package URL](https://www.packageurl.org), which is a generic way to refer to software packages. Note that as of the time of this writing, only the github and npm types are supported, if your code comes from somewhere else, you'll need to provide an URL to the package in `download_url`.

If you have to deal with many vendored files, you might want to organize things by directory, and in the check also use directory based origins. The above example could also be organized as:

    /external/bootstrap/js/bootstrap.js
    /external/bootstrap/css/bootstrap.css

and your `/external/vendor-libs.json` look like this:

```json
{
    "bootstrap": {
        "purl": "pkg:github/twbs/bootstrap@v5.3.8#dist"
    }
}
```

meaning: Compare the local directory `bootstrap` with the `dist` folder from github repository twbs/bootstrap at version v5.3.8.

Note that the version tags used here are for readability, in production you should use commit hashes as they are less mutable than tags. Also prefer git purls over npm ones if you can, for the same reason.

Github Action
-------------

After you've supplied the `vendor-libs.json` file, you can activate the action in some github workflow, for the above example you'd add

```yaml
- name: Check vendor libs
  uses: oca/check-vendor-libs@v1
  with:
    directories: "*/static/lib"
```

Local testing
-------------

To validate vendored files locally, you can pip install this repository, and for the above example, call

```shell
check-vendor-libs external
```

which will download the code as defined in `external/vendor-libs.json` to `~/.cache/check-vendor-libs` and show possible divergences. If nothing is returned, all is good.
