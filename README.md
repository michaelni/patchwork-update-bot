# patchwork-update-bot
Script to automate some patchwork patch state maintaince.

This is one of several scripts used for maintaining FFmpegs patchwork. But
its Project unspecific so should be usable for other projects.

It can detect superseeded patches by subject and author, applied patches by
subject matched up to git, non applicable patches that are produced by
FFmpegs self tests.

This needs python and pwclient with setup access to the patchwork server.
Run this script from a checked out git repository so that commands like "git log"
relate to pwclients output.

It will cache patches in a pwubot.cache file so as not to download them twice.

Pull requests and patches per email are welcome.
