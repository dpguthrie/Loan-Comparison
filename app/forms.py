from flask_wtf import Form
from wtforms import DecimalField, IntegerField
from wtforms.validators import DataRequired


class LoanForm(Form):
    Amount = DecimalField("Commitment Amount", validators=[DataRequired("Please enter an amount")])
    Term = IntegerField("Term (Months)", validators=[DataRequired("Please enter the loan term (in years)")])
    Amort = IntegerField("Amortization (Months)", validators=[DataRequired("Please enter the loan amortization (in years)")])
    Rate = DecimalField("Interest Rate", validators=[DataRequired("Please enter the loan's interest rate")])
    Reset = IntegerField("Rate Reset (Month)", validators=[DataRequired("Please enter the month the rate resets")])
