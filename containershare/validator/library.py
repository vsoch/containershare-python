'''

validators/library.py: python functions to validate library

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
from containershare.utils import read_yaml
from glob import glob
from .utils import ( notvalid, validate_url )


class LibraryValidator:

    def __init__(self,quiet=False):
        if quiet is True:
            bot.level = 0

    def __str__(self):
        return "containershare.LibraryValidator"

    def validate(self, ymlfile):
        bot.test('CONTAINER: %s' % os.path.basename(ymlfile))
        if ymlfile.endswith('md'):
            if not self._validate_markdown(ymlfile):
                return False
        else:
            print('Invalid extension %s, %s must be markdown (.md)' % ymlfile)
            return False
        return True

    def _print_valid(self, result):
        options = {True:'yes', False: 'no'}
        return options[result]

    def _validate_markdown(self, ymlfile):
        '''ensure that fields are present in markdown file'''

        try:
            import yaml
        except:
            bot.error('Python yaml is required for testing yml/markdown files.')
            sys.exit(1)

        uid = os.path.basename(ymlfile).strip('.md')
     
        if os.path.exists(ymlfile):

            self.metadata = read_yaml(ymlfile)
       
            # Required fields for library
            fields = ['github',
                      'docker',
                      'web',
                      'name',
                      'tags',
                      'uid',
                      'maintainer']

            # Tests for all fields
            for field in fields:
                if field not in self.metadata:
                    print('%s is missing field %s.' %(uid, field))
                    return False
                if self.metadata[field] in ['',None]:
                    return False

            # Uid in file must match filename
            if self.metadata['uid'] != uid:
                print('Mismatch in file %s.md and %s.' %(ymlfile, 
                                                         self.metadata['uid'])) 
                return False

            # Ensure that urls are from Docker Hub and Github
            if 'github' not in self.metadata['github']:
                return notvalid('%s: not a valid github repository' % name)
            if 'hub.docker.com' not in self.metadata['docker']:
                return notvalid('%s: not a valid github repository' % name)

            # Tags must be in a list
            if not isinstance(self.metadata['tags'],list):
                return notvalid('%s: tags must be a list' % name)

            # Validate that links are correct urls
            for key in ['web', 'github', 'docker']:
                url = self.metadata[key]
                if not validate_url(url):
                    return notvalid('%s is not a valid URL.' %(url))

            # Validate name
            bot.test("        Name: %s" % self.metadata['name'])

            if not re.match("^[a-z0-9_-]*$", self.metadata['name']): 
                return notvalid('''invalid characters in %s, only 
                               lowercase and "-" or "_" allowed.''' %(content['name'])) 


        return True
