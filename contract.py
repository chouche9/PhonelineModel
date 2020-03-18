"""
CSC148, Winter 2019
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2019 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call


# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This is an abstract class. Only subclasses should be instantiated.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.datetime
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class MTMContract(Contract):
    """A month to month contract for the phone line

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """

    start: datetime.datetime
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        Contract.__init__(self, start)

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        self.bill = bill
        self.bill.set_rates("MTM", MTM_MINS_COST)
        self.bill.add_fixed_cost(MTM_MONTHLY_FEE)


class TermContract(Contract):
    """A term contract

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    end:
        ending date for the contract
    _datelist:
        list of all the month+year combination of the contract's bill
    """
    start: datetime.datetime
    bill: Optional[Bill]
    end: datetime.datetime
    _datelist: list

    def __init__(self, start: datetime.date, end: datetime.date) -> None:
        Contract.__init__(self, start)
        self.end = end
        self._datelist = []

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        if self.start.month == month:
            self.bill = bill
            self.bill.set_rates("TERM", TERM_MINS_COST)
            self.bill.add_fixed_cost(TERM_MONTHLY_FEE + TERM_DEPOSIT)
            self._datelist.append((month, year))
        else:
            self.bill = bill
            self.bill.set_rates("TERM", TERM_MINS_COST)
            self.bill.add_fixed_cost(TERM_MONTHLY_FEE)
            self._datelist.append((month, year))

    def bill_call(self, call: Call) -> None:
        """Override the inherited method from the Contract class. Ensure that
        the free minutes are used up first before adding to billed minutes.
        """
        # self.bill.free_min = 1
        duration_min = ceil(call.duration / 60.0)
        if self.bill.free_min < TERM_MINS:
            if (self.bill.free_min + duration_min) <= TERM_MINS:
                self.bill.add_free_minutes(duration_min)
            elif (self.bill.free_min + duration_min) > TERM_MINS:
                self.bill.add_billed_minutes(self.bill.free_min +
                                             duration_min - TERM_MINS)
                self.bill.free_min = 100
        elif self.bill.free_min == TERM_MINS:
            self.bill.add_billed_minutes(duration_min)

    def cancel_contract(self) -> float:
        """Override the inherited method from the Contract Class. If contract
         is cancelled before the term end date, the term deposit is forfeited;
         otherwise, the term deposit is returned."""
        if self._datelist[-1][1] > self.end.year:
            self.start = None
            self.bill.add_fixed_cost(-TERM_DEPOSIT)
            return self.bill.get_cost()
        elif self._datelist[-1][1] == self.end.year and self._datelist[-1][0] >\
                self.end.month:
            self.start = None
            self.bill.add_fixed_cost(-TERM_DEPOSIT)
            return self.bill.get_cost()
        else:
            self.start = None
            return self.bill.get_cost()


class PrepaidContract(Contract):
    """a prepaid contract

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    balance:
        a total balance of the contract that is carried over every new month
    """
    start: datetime.datetime
    bill: Optional[Bill]
    balance: int

    def __init__(self, start: datetime.date, balance: int) -> None:
        """Precondition: balance is initially negative"""
        Contract.__init__(self, start)
        self.balance = -balance

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        if self.bill is None:
            # check for top-up in first month(regardless of same month or not)
            if self.balance > -10:
                self.balance += -25
            initial_bal = self.balance
            self.bill = bill
            self.bill.set_rates("PREPAID", PREPAID_MINS_COST)
            self.bill.add_fixed_cost(initial_bal)
        else:
            self.balance = self.bill.get_cost()
            if self.balance > -10:
                self.balance += -25
            last_month_bal = self.balance
            self.bill = bill
            self.bill.set_rates("PREPAID", PREPAID_MINS_COST)
            self.bill.add_fixed_cost(last_month_bal)

    def cancel_contract(self) -> float:
        self.balance = self.bill.get_cost()
        if self.balance > 0:
            return self.balance
        else:
            return 0


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
