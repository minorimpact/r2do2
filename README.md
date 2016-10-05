# r2do2
A very simple task manager built on Flask and SQLAlchemy.

## Description
Not intended for serious use, r2do2 is a python learning experiment based in no small part on 
Miguel Grinberg's [Flask Mega Tutorial](http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world).

## Installation
~~~~~
git clone git@github:minorimpact/r2do2
cd r2do2
export R2DO2_DB_PASSWORD=r2do2password
export R2DO2_DB_SERVER=db.example.com
./run.py
~~~~~

## Known Bugs/Issues
* Only works with mysql
* Featureless.
* Users can't change their passwords or set an actual avatar.
