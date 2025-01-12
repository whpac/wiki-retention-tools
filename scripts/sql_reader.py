import sqlparse

def readSqlDump(sqlDumpFile):
    '''
    This is the main function for reading MediaWiki SQL dumps.
    It reads the SQL dump file statement by statement and yields the records
    that are inserted into the tables.
    This function operates in a streaming mode, meaning it should be safe
    to use it with large SQL dumps.
    Every record is returnes as a dict object, with the column names as keys.
    An additional key '$table' is added to the dict, which contains the table name,
    in case the dump contains records from multiple tables.
    '''
    tables = {}

    for sqlChunk in readStatements(sqlDumpFile):
        # Parse the SQL statement
        parsed = sqlparse.parse(sqlChunk)
        for statement in parsed:
            stype = statement.get_type()
            # Deliberately ignore DROP statements, they add no information
            if stype == 'UNKNOWN' or stype == 'DROP':
                continue
            elif stype == 'CREATE':
                tableName, columns = processCreateTable(statement)
                tables[tableName] = columns
            elif stype == 'INSERT':
                for record in processInsert(statement, tables):
                    yield record
            else:
                print('Unknown statement type: ' + statement.get_type())


def readStatements(file):
    # Accumulate the lines until we have a line ending with semicolon
    # This is a heuristic to read the statements one-by-one
    # (or at least, not all at once)
    chunk = ''
    for line in file:
        chunk += line
        if chunk.endswith(';\n'):
            yield chunk
            chunk = ''

    # If there is a last chunk, emit it
    if chunk:
        yield chunk


def processCreateTable(statement):
    tableName = ''
    columns = []

    for token in statement.tokens:
        if token.ttype == sqlparse.tokens.Whitespace:
            continue
        elif isinstance(token, sqlparse.sql.Identifier) and tableName == '':
            tableName = token.get_real_name()
        elif isinstance(token, sqlparse.sql.Parenthesis):
            columns = processCreateTableColumnList(token.flatten())

        if tableName and columns:
            break

    return tableName, columns


def processCreateTableColumnList(defTokens):
    columnSpecifiers = [[]]
    columnNames = []
    parenDepth = -1 # We start at -1 because the first parenthesis is the CREATE TABLE's one
    for token in defTokens:
        if token.match(sqlparse.tokens.Punctuation, '('):
            parenDepth += 1
            if parenDepth == 0:
                continue # Don't include the outer parenthesis in the column specifiers
        elif token.match(sqlparse.tokens.Punctuation, ')'):
            parenDepth -= 1
            if parenDepth == -1:
                break

        if token.match(sqlparse.tokens.Punctuation, ',') and parenDepth == 0:
            columnSpecifiers.append([])
            continue

        columnSpecifiers[-1].append(token)

    for specifier in columnSpecifiers:
        for token in specifier:
            if token.ttype == sqlparse.tokens.Whitespace:
                continue
            if token.ttype == sqlparse.tokens.Newline:
                continue

            # The column name will be the first non-empty token
            if token.ttype == sqlparse.tokens.Name:
                colName = token.value
                if colName.startswith('`') and colName.endswith('`'):
                    colName = colName[1:-1]
                columnNames.append(colName)
            break
    
    return columnNames


def processInsert(statement, knownTables):
    tableName = ''
    columns = []

    for token in statement.tokens:
        if token.ttype == sqlparse.tokens.Whitespace:
            continue
        elif isinstance(token, sqlparse.sql.Identifier) and tableName == '':
            tableName = token.get_real_name()
            columns = knownTables[tableName]
        elif isinstance(token, sqlparse.sql.Values):
            for row in processInsertValues(list(token.flatten())):
                record = {col: val for col, val in zip(columns, row)}
                record['$table'] = tableName
                yield record


def processInsertValues(valuesTokens):
    rowValues = []
    for token in valuesTokens:
        if token.match(sqlparse.tokens.Keyword, 'VALUES'):
            continue
        if token.ttype == sqlparse.tokens.Whitespace:
            continue

        if token.match(sqlparse.tokens.Punctuation, ')'):
            yield rowValues
            rowValues = []
        if token.ttype == sqlparse.tokens.Punctuation:
            continue

        if token.ttype == sqlparse.tokens.Literal.String.Single:
            s = token.value[1:-1]
            s = s.replace("\\'", "'")
            rowValues.append(s)
        elif token.ttype == sqlparse.tokens.Literal.Number.Integer:
            rowValues.append(int(token.value))
        elif token.match(sqlparse.tokens.Keyword, 'NULL'):
            rowValues.append(None)
        else:
            rowValues.append((token.ttype, token.value))
