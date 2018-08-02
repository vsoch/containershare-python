'''

validators/runtime.py: python functions to validate deployments

Copyright (c) 2018, Vanessa Sochat
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''

import os
import re
import sys
from containershare.logger import bot
from containershare.utils import ( clone, read_file )
from .utils import notvalid
import requests
import tempfile
from glob import glob


class RuntimeValidator:

    def __init__(self,quiet=False):
        if quiet is True:
            bot.level = 0

    def __str__(self):
        return "containershare.RuntimeValidator"

    def validate(self, url):
        ''' takes in a Github repository for validation of preview and 
            runtime (and possibly tests passing?
        '''

        # Preview must provide the live URL of the repository
        if not url.startswith('http') or not 'github' in url:
            bot.error('Test of preview must be given a Github repostitory.')
            return False

        if not self._validate_preview(url):
            return False

        return True

    def _print_valid(self, result):
        options = {True:'yes', False: 'no'}
        return options[result]

    def validate_url(self, url):

        bot.test('url: %s' %url)
        response = requests.get(url)

        if response.status_code == 404:
            bot.error('%s not found.' % url)
            return False 
        return True

    def _validate_preview(self, url):

        bot.test('Container url: %s' %url)
        org,repo = url.split('/')[-2:]
        if repo.endswith('.git'):
            repo = repo.replace('.git','')
        github_pages =  "https://%s.github.io/%s" %(org,repo)

        # Save Github pages for comparison with record
        self.github_pages = github_pages

        bot.test('Github Pages url: %s' %github_pages)

        response = requests.get(github_pages)

        if response.status_code == 404:
            bot.error('''Preview not found at %s. You must publish a static 
                         preview from the gh-pages branch of your repository to
                         add to the library.''' % github_pages)
            return False 

        index = response.text
        tmpdir = tempfile.mkdtemp()
        ghpages = clone(url, tmpdir, branch='gh-pages')
        contenders = glob('%s/*' %ghpages)
        license = False
        found = False
        tags = False
        valid = True

        # Required to have at least one latest
        manifest = False
        inspect = False

        for test in contenders:
            if os.path.isdir(test):
                continue

            print('...%s' %test)
            if "LICENSE" in os.path.basename(test):
                license = True
            if os.path.basename(test) == "index.html":
                bot.test('Found index file in repository.')
                found = True
            if os.path.basename(test) == 'tags.json':
                bot.test('Found tags manifest in repository.')
                tags = True
            if os.path.basename(test) == 'manifest-latest.json':
                bot.test('Found latest manifest in repository.')
                manifest = True
            if os.path.basename(test) == 'inspect.json':
                bot.test('Found latest inspection in repository.')
                inspect = True

        # These are all required!
        if license is False:
            bot.warning("LICENSE file not found, please add a LICENSE")
            valid = False
        if tags is False:
            bot.warning("inspect-latest.json not found, required.")
            valid = False

        if manifest is False:
            bot.warning("manifest-latest.json not found, required")
            valid = False

        self._print_valid(valid)
        return valid
