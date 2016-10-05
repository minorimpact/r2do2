#!/usr/bin/python

# pybabel extract -F babel.cfg -o messages.pot app
# pybabel init -i messages.pot -d app/translations -l es
# vi app/translations/es/LC_MESSAGES/messages.po
# pybabel compile -d app/translations
#
# pybabel extract -F babel.cfg -o messages.pot app
# pybabel update -i messages.pot -d app/translations
# vi app/translations/es/LC_MESSAGES/messages.po
# pybabel compile -d app/translations

from app import app
app.run(host="0.0.0.0", debug=True)
