import csv

from ofxstatement import statement
from ofxstatement.parser import CsvStatementParser
from ofxstatement.plugin import Plugin
from ofxstatement.parser import StatementParser
from ofxstatement.statement import StatementLine


class bnpPlugin(Plugin):
    """Belgian BNP Paribas Fortis
    """

    def get_parser(self, filename):
        f = open(filename, 'r', encoding="utf-8")
        parser = bnpParser(f)
        parser.statement.bank_id = "Bnp"
        parser.statement.currency = "EUR"
        return parser


class bnpParser(CsvStatementParser):

    date_format = "%d/%m/%Y"

    mappings = {
        'id': 0,
        'date': 1,
        'check_no': 0,
        'amount': 3,
    }

    def parse(self):
        """Main entry point for parsers
        super() implementation will call to split_records and parse_record to
        process the file.
        """
        stmt = super(bnpParser, self).parse()
        statement.recalculate_balance(stmt)
        return stmt

    def split_records(self):
        """Return iterable object consisting of a line per transaction
        """
        reader = csv.reader(self.fin, delimiter=";")
        next(reader, None)
        return reader

    def parse_record(self, line):
        """Parse given transaction line and return StatementLine object
        """

        stmtline = super(bnpParser, self).parse_record(line)
        stmtline.trntype = 'DEBIT' if stmtline.amount < 0 else 'CREDIT'

        # Raise an exception if we have statements for more than one account
        if (self.statement.account_id == None):
            self.statement.account_id = line[5]
        elif (self.statement.account_id != line[5]):
            raise ValueError("CSV file contains multiple accounts")

        payee = line[8]
        if payee != "":
            payee += " -- "

        memo = payee + line[9]
        stmtline.memo = memo

        if memo != "":
            memo = " -- " + memo
        description = line[10] + memo
        stmtline.payee = description  # gnucash treats payee as description
        return stmtline
