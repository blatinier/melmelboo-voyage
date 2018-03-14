#!/usr/bin/env bash
sqlite3 /var/www/voyage/blog/content/data/ghost.db "update posts set status='published' where published_at < datetime('now', 'localtime') and status='scheduled'"
