project-x
=========

Pulls logs from an IMAP folder and extracts them locally for better searching

## Usage

1. Set up whatever you'd like to ship logs to your email address
 * the logs should be in an attached tarball
 * logpull doesn't care what you set your subject/body to, but you can use them to filter the correct mail into a single mail folder
2. Copy config.yaml.example to config.yaml
3. Edit it with the correct host/username/password and labels
4. When run, pull.py will extract the logs to the first path and symlink the other paths to that location
5. Grep away!

## Installation

   git clone git://github.com/akerl/logpull

## License

logpull is released under the MIT License. See the bundled LICENSE file for
details.

