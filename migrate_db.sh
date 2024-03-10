#!/bin/sh

flask  migrate -m "Migration"
flask migrate upgrade
