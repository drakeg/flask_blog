#!/bin/sh

flask db migrate -m "Migration"
flask db upgrade
