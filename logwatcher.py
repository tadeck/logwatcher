#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
try:
    import sqlite3
except (ImportError):
    import sqlite as sqlite3


LOG_START_PAT = '(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})[-+]\d{2}:\d{2}: (\w+):'
_db_name = 'logwatch'
_log_display_format = '[ID: "{0}", Type: "{1}", Date: "{2}"]\n\nContent: {3}'


def clear_table():
    conn = sqlite3.Connection(_db_name)
    c = conn.cursor()
    c.execute('DELETE FROM `logs`')
    result = c.fetchall()
    conn.commit()
    return result


def get_last():
    conn = sqlite3.Connection(_db_name)
    c = conn.cursor()
    sql_query = '''SELECT `id`, `type`, `date`, `content`
        FROM `logs`
        ORDER BY `id` DESC
        LIMIT 1'''
    c.execute(sql_query)
    return c.fetchone()


def init_database():
    conn = sqlite3.Connection(_db_name)
    c = conn.cursor()
    sql_command = '''CREATE TABLE `logs` (
        `id` INTEGER PRIMARY KEY,
        `type` TEXT,
        `date` TEXT,
        `content` TEXT
    )'''
    try:
        result = c.execute(sql_command)
    except (sqlite3.OperationalError):
        result = False
    conn.commit()
    return result


def log_search(query_params):
    conn = sqlite3.Connection(_db_name)
    c = conn.cursor()
    sql_command = '''SELECT `id`, `type`, `date`, `content`
        FROM `logs`
        '''
    begins_with_keyword = any([
        query_params.lower().startswith('where '),
        query_params.lower().startswith('order '),
        query_params.lower().startswith('group '),
        query_params.lower().startswith('limit ')
    ])
    if not begins_with_keyword:
        sql_command += ' WHERE '
    sql_command += query_params
    c.execute(sql_command)
    return c.fetchall()


def save_log(log, cursor=None):
    '''Saves log to the database. Log is passed as dictionary.    
    '''
    log['content'] = log['content'].strip(' \n')
    if cursor:
        params = (log['type'], log['date'], log['content'])
        sql_command = '''INSERT INTO `logs` (`type`,`date`,`content`)
            VALUES (?, ?, ?)'''
        result = cursor.execute(sql_command, params)
        return result
    else:
        print '"{type}" log dated "{date}" was:\n\n{content}\n'.format(**log)
        return False # not saved, only outputted


def process_file(log_filename):
    conn = sqlite3.Connection(_db_name)
    cursor = conn.cursor()
    with open(log_filename) as log_file:
        i = 1  # lines count
        lc = 0  # logs count
        cur_log = {}
        proc_status_fmt = '\r{} lines processed, {} logs found'
        while True:
            line = log_file.readline()
            if not line:
                break
            match = re.match(LOG_START_PAT, line)
            if match:
                if cur_log:
                    save_log(cur_log, cursor)
                    lc += 1
                    cur_log = {}
                cur_log['date'] = match.group(1)
                cur_log['type'] = match.group(2)
                cur_log['content'] = ' '.join(line.split(' ')[2:]).lstrip(' \n')
            elif cur_log:
                cur_log['content'] += line
            else:
                print 'STRANGE'
                raise KeyboardInterrupt
            i += 1
            # print 'Line no. {} processed'.format(i)
            sys.stdout.flush()
            sys.stdout.write(proc_status_fmt.format(i, lc))
    conn.commit()
    conn.close()
    print
    print 'Finished processing log file.'


def show_help(subc=None):
    docs = {
        'init': 'Initialize the database by creating table and file',
        'clear': 'Delete logs from database',
        'process': 'Process the filename given as parameter and save logs',
        'last': 'Show last log from the database',
        'search': 'Search logs by giving SQLite condition as parameter'
    }
    if subc:
        try:
            print '"{} {}": {}'.format(sys.argv[0], subc, docs[subc])
        except (KeyError):
            print 'Command or help for this command does not exist'
    else:
        print 'Possible commands: {}'.format(', '.join(docs))


def main():
    try:
        command = sys.argv[1]
    except (IndexError):
        command = None
    if command == 'init':
        if init_database():
            print 'Database initialized'
        else:
            print 'Database has not been initialized'
    elif command == 'clear':
        result = clear_table()
        print 'Cleared the table'
    elif command == 'process':
        try:
            process_file(sys.argv[2])
        except (IndexError):
            frmt = 'Provide name of the file to be processed: "{} {} {}"'
            repls = (sys.argv[0], command, 'filename.log')
            print frmt.format(*repls)
    elif command == 'last':
        last_log = get_last()
        if last_log:
            print _log_display_format.format(*last_log)
        else:
            print 'No logs have been found'
    elif command == 'search':
        result = log_search(' '.join(sys.argv[2:]))
        if result:
            for row in result:
                print _log_display_format.format(*row) + '\n' + '=' * 60
        else:
            print 'No results found'
    elif command == 'help':
        show_help(sys.argv[2] if sys.argv[2:3] else None)
    else:
        if command:
            print 'Unsupported command: "{}"'.format(command)
        else:
            print 'Provide some command to be executed'
        show_help()

if __name__ == '__main__':
    start_time = time.time()
    main()
    print '(Execution time: {} seconds)'.format(time.time() - start_time)
