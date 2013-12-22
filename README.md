logpull
=========

Pulls logs from an IMAP folder and extracts them locally for better searching

## Usage

1. Set up whatever you'd like to ship logs to your email address
 * the logs should be in an attached tarball
 * logpull doesn't care what you set your subject/body to, but you can use them to filter the correct mail into a single mail folder
2. Copy config.yaml.example to config.yaml
3. Edit it with the correct host/username/password and labels
4. When run, logpull.py will extract the logs to the first path and symlink the other paths to that location
5. Grep away!

### Alternate Password Sources

Keeping the password in the yaml file doesn't make me happy, so logpull supports stashing the password elsewhere.

To do this, just specify "password\_method: name" in the config file rather than providing a password.

#### OSX Keychain

In Keychain Access, select File -> New Password Item. The Keychain Item Name should be "logpull", and the account name should be your IMAP username.

This uses the `security` CLI interface for keychain, so you'll get a popup asking for permission to access the keychain data when running pull.py

## Installation

   git clone git://github.com/akerl/logpull

## License

logpull is released under the MIT License. See the bundled LICENSE file for details.

