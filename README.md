Very first, very rough version of LogWatcher.

The main goal of this script is to turn raw, flat text files with logs into
searchable, structured data in form of SQLite database.

It provides command-line interface for quick processing of log files and
further analysis based on SQLite queries provided within command line.

Example usage:

1. Initialize database:

        ./logwatcher.py init

2. Turn raw files into databases (`filename.log` is the name of the log file):

        ./logwatcher.py process filename.log

3. Check the last log entry:

        ./logwatcher.py last

4. Make searches within logs, such as:

        ./logwatcher.py search id=3
        ./logwatcher.py search content LIKE \"%Fatal%\"
        ./logwatcher.py search ORDER BY id DESC LIMIT 10
        ./logwatcher.py search id IN (3, 40, 56)
        ./logwatcher.py search date=\"2011-12-31T12:13:14\"

5. Clear database from log entries:

        ./logwatcher.py clear
