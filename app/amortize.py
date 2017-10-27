import pandas as pd
from datetime import date
import numpy as np
from collections import OrderedDict
from dateutil.relativedelta import *


def amortize(amount, rate, term, amort, reset=0, proxy=None, rate_type='F', start_date=date.today(), annual_payments=12):
    """
    Calculate amortization schedule given loan details
    
    Arguments:
        amount {[float]} -- Initial amount of loan
        rate {[float]} -- Initial rate of loan
        term {[int]} -- Term of loan (in months)
        amort {[int]} -- Amortization period of loan (in months)
    
    Keyword Arguments:
        reset {int} -- Month in which rate will reset at rate + proxy[month] (default: {0})
        proxy {[array]} -- Array element of rate increases/decreases
        rate_type {str} -- Either a fixed or variable loan (default: {'F'})
        start_date {[date]} -- Beginning date of loan (default: {date.today()})
        annual_payments {number} -- Number of payments in a year (default: {12})
    """

    p = 1
    beg_balance = amount
    end_balance = amount
    new_rate = rate

    # Calculate payment amount for loan
    pmt = -round(np.pmt(new_rate/annual_payments, amort, amount), 2)

    if rate_type == 'F':

        while end_balance > 0:

            # Recalculate the interest based on the current balance
            interest = round(((new_rate/annual_payments) * beg_balance), 2)

            # Determine payment amount based on end of term, rate reset
            if p == term:
                principal = beg_balance
            elif p == reset:
                new_rate = rate + proxy[p - 1]
                pmt = -round(np.pmt(new_rate/annual_payments, (amort - p + 1), beg_balance), 2)
                interest = round(((new_rate/annual_payments) * beg_balance), 2)
                principal = pmt - interest
            else:
                pmt = min(pmt, beg_balance + interest)
                principal = pmt - interest

            end_balance = beg_balance - principal

            yield OrderedDict([('Month',start_date),
                               ('Period', p),
                               ('Begin Balance', beg_balance),
                               ('Payment', pmt),
                               ('Principal', principal),
                               ('Interest', interest),
                               ('Interest Rate', new_rate),
                               ('End Balance', end_balance)])

            # Increment the counter, balance and date.
            p += 1
            if p > term:
                break
            start_date += relativedelta(months=1)
            beg_balance = end_balance
    else:

        while end_balance > 0:

            if p == term:
                new_rate = rate + proxy[p - 1]
                principal = beg_balance
                interest = round(((new_rate/annual_payments) * beg_balance), 2)
            else:
                new_rate = rate + proxy[p - 1]
                interest = round(((new_rate/annual_payments) * beg_balance), 2)
                principal = pmt - interest

            end_balance = beg_balance - principal

            yield OrderedDict([('Month',start_date),
                               ('Period', p),
                               ('Begin Balance', beg_balance),
                               ('Payment', pmt),
                               ('Principal', principal),
                               ('Interest', interest),
                               ('Interest Rate', new_rate),
                               ('End Balance', end_balance)])

            # Increment the counter, balance and date.
            p += 1
            if p > term:
                break
            start_date += relativedelta(months=1)
            beg_balance = end_balance


def amortization_table(amount, rate, term, amort, reset=0, proxy=None, rate_type='F', loan_type = None, start_date=date.today(), annual_payments=12 ):
    """
    Calculate the amortization schedule given the loan details as well as summary stats for the loan

    :param principal: Amount borrowed
    :param interest_rate: The annual interest rate for this loan
    :param years: Number of years for the loan
    
    :param annual_payments (optional): Number of payments in a year. DEfault 12.
    :param addl_principal (optional): Additional payments to be made each period. Default 0.
    :param start_date (optional): Start date. Default first of next month if none provided

    :return: 
        schedule: Amortization schedule as a pandas dataframe
        stats: Pandas dataframe that summarizes the payoff information
        total_int_income:  Cumulative interest for loan
    """
    
    # Generate the schedule and order the resulting columns for convenience
    schedule = pd.DataFrame(amortize(amount, rate, term, amort, reset, proxy,
                                     rate_type, start_date, annual_payments))
    schedule = schedule[["Period", "Month", "Begin Balance", "Payment", "Interest", 
                         "Principal", "Interest Rate", "End Balance"]]
    
    # Convert to a datetime object to make subsequent calcs easier
    schedule["Month"] = pd.to_datetime(schedule["Month"])

    # Create cumulative interest column
    schedule["Cumulative Interest"] = schedule.Interest.cumsum()
    
    #Create a summary statistics table
    payoff_date = schedule["Month"].iloc[-1]
    remaining_principal = schedule["Principal"].iloc[-1]
    stats = pd.Series([loan_type, payoff_date, schedule["Period"].count(), rate*100,
                       term, amount, schedule["Payment"].mean(), remaining_principal,
                       schedule["Interest"].sum()],
                       index=["Loan Type", "Payoff Date", "Num Payments", "Interest Rate", "Months", "Principal",
                             "Avg Payment", "Remaining Principal", "Total Interest"])
    total_int_income = schedule["Cumulative Interest"]
    
    return schedule, stats, total_int_income


# TODO: Pull rates from database

proxy_rates = [0,
0,
0,
0.0025,
0.0025,
0.0025,
0.0025,
0.005,
0.005,
0.005,
0.005,
0.0075,
0.0075,
0.0075,
0.0075,
0.0075,
0.01,
0.01,
0.01,
0.01,
0.01,
0.01,
0.0125,
0.0125,
0.0125,
0.0125,
0.0125,
0.0125,
0.0125,
0.0125,
0.0125,
0.0125,
0.0125,
0.0125,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015,
0.015]
