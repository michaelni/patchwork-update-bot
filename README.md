# patchwork-update-bot
Script to automate some patchwork patch state maintaince

This needs python and pwclient with setup access to the patchwork server
run this script from a checked out git repository so that commands like "git log"
relate to pwclients output

It will cache patches in a pwubot.cache file so as not to download them twice
