# views.py

from flask import render_template, request

from app import app
from .forms import LoanForm
from .amortize import amortize, amortization_table, proxy_rates
from scipy.optimize import minimize
import pandas as pd
from collections import OrderedDict
import plotly
import json

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        # Create dictionary with form values
        l1 = { "amount": float(request.form['Amount']),
               "rate": float(request.form['Rate'])/100.0,
               "term": int(request.form['Term']),
               "amort": int(request.form['Amort']),
               "reset": int(request.form['Reset']),
               "proxy": proxy_rates,
               "rate_type": "F" }

        # Define objective function
        def objective(x):
            am1, s1, ii1 = amortization_table(l1['amount'], l1['rate'], l1['term'], l1['amort'], reset = l1['reset'], proxy = l1['proxy'], rate_type = l1['rate_type'])
            am2, s2, ii2 = amortization_table(l1['amount'], x[0], l1['term'], l1['amort'])
            am3, s3, ii3 = amortization_table(l1['amount'], x[1], l1['term'], l1['amort'], proxy = l1['proxy'], rate_type = 'V')

            i1 = ii1.iloc[-1]
            i2 = ii2.iloc[-1]
            i3 = ii3.iloc[-1]

            ls = [i1, i2, i3]
            ls_count = len(ls)
            ls_mean = sum(ls) / ls_count
            diff = [x - ls_mean for x in ls]
            sq_diff = [d ** 2 for d in diff]

            return sum(sq_diff)

        # Initialize Guesses in Minimize Function
        x0 = [.04,.04]

        # Assign results of minimize function to 'res' variable
        res = minimize(objective, x0, method='COBYLA', options={'tol': 1e-7})

        # Obtain amortization table, stats table, and total interest income for each scenario
        am1, s1, ii1 = amortization_table(l1['amount'], l1['rate'], l1['term'], l1['amort'], reset = l1['reset'], proxy = l1['proxy'], rate_type = l1['rate_type'], loan_type = 'Fixed with Reset')
        am2, s2, ii2 = amortization_table(l1['amount'], res.x[0], l1['term'], l1['amort'], loan_type = 'Fixed')
        am3, s3, ii3 = amortization_table(l1['amount'], res.x[1], l1['term'], l1['amort'], proxy = l1['proxy'], rate_type = 'V', loan_type = 'Variable')

        # Create interest rate dictionary
        IRdict = OrderedDict()
        IRdict['Variable'] = [s3['Interest Rate'], 'variable-color']
        IRdict['Reset'] = [s1['Interest Rate'], 'reset-color']
        IRdict['Fixed'] = [s2['Interest Rate'], 'fixed-color']
        min_pmt = min([am1['Payment'].iloc[0], am2['Payment'].iloc[0], am3['Payment'].iloc[0]])
        max_pmt = max([am1['Payment'].iloc[0], am2['Payment'].iloc[0], am3['Payment'].iloc[0]])
        principal_gap = max([am1['Begin Balance'].iloc[-1], am2['Begin Balance'].iloc[-1], am3['Begin Balance'].iloc[-1]]) - min([am1['Begin Balance'].iloc[-1], am2['Begin Balance'].iloc[-1], am3['Begin Balance'].iloc[-1]])


        # 
        min_rate = "{:.2f}".format(IRdict[min(IRdict.keys(), key=(lambda k: IRdict[k]))][0])
        max_rate = "{:.2f}".format(IRdict[max(IRdict.keys(), key=(lambda k: IRdict[k]))][0])
        gap = ii2[int(request.form['Reset'])-2] - ii1[int(request.form['Reset'])-2]

        try:
            var_grtr = [x for x in am3['Interest Rate'].iteritems() if x[1] > s2['Interest Rate']/100][0][0]+1
            ir_desc = (
                'Proposed interest rates range from {min_rate}% to {max_rate}%, ({min_key} - {max_key}).'
                '  However, the interest rate on the variable-rate loan becomes greater than the interest rate'
                ' on the fixed-rate loan at {var_grtr} months.  At {reset} months, the interest rate on the '
                'loan with a rate reset jumps to {reset_rate}%.'.format(
                    min_rate = str(min_rate), max_rate = str(max_rate), 
                    min_key = min(IRdict.keys(), key=(lambda k: IRdict[k])),
                    max_key = max(IRdict.keys(), key=(lambda k: IRdict[k])),
                    var_grtr = var_grtr, reset = str(int(request.form['Reset'])),
                    reset_rate = str("{:.2f}".format(am1['Interest Rate'].iloc[-1]*100)))
            )
        except IndexError:
            ir_desc = (
                'Proposed interest rates range from {min_rate}% to {max_rate}%, ({min_key} - {max_key}).  '
                'The interest rate on the variable-rate loan peaks at {var_rate}%, slightly below the interest rate on the fixed-rate loan.  '
                'At {reset} months, the interest rate on the loan with a rate reset jumpts to {rate_reset}%.'.format(
                    min_rate = str(min_rate), max_rate = str(max_rate), 
                    min_key = min(IRdict.keys(), key=(lambda k: IRdict[k])),
                    max_key = max(IRdict.keys(), key=(lambda k: IRdict[k])),
                    var_rate = str("{:.2f}".format(am3['Interest Rate'].iloc[-1]*100)), reset = str(int(request.form['Reset'])),
                    rate_reset = str("{:.2f}".format(am1['Interest Rate'].iloc[-1]*100)))
            )

        int_income_desc = (
            'At the end of month {term}, each loan will have yielded ${int_income} in interest income.  '
            'The greatest gap in interest income occurs just prior to the rate reset at {reset} months, a '
            'total of ${gap}'.format(
                term = request.form['Term'], int_income = "{:,.0f}".format(ii1.iloc[-1]),
                reset = str(int(request.form['Reset'])-1), gap = "{:,.0f}".format(gap))
        )

        payment_desc = (
            'Monthly payment amounts range from ${min_pmt} to ${max_pmt} at loan origination.  '
            'However, that gap increases at {reset} months when the interest rate on the loan with a reset '
            'jumps, increasing the payment amount from ${reset_min_pmt} to ${reset_max_pmt}.'.format(
                min_pmt = str("{:,.0f}".format(min_pmt)), max_pmt = str("{:,.0f}".format(max_pmt)), 
                reset = request.form['Reset'], reset_min_pmt = str("{:,.0f}".format(am1['Payment'].iloc[int(request.form['Reset'])-2])),
                reset_max_pmt = str("{:,.0f}".format(am1['Payment'].iloc[int(request.form['Reset'])-1]))
            )
        )

        principal_desc = (
            'As interest rates increase, the gap between the remaining principal on the variable-rate loan and '
            'both fixed-rate loans also increase.  Because the payment amount for the variable-rate loan remains static, '
            'less and less of the payment is applied toward principal.  The gap at maturity is ${principal_gap}.'.format(
                principal_gap = str("{:,.0f}".format(principal_gap))
            )
        )

        desc_list = [ir_desc, int_income_desc, payment_desc, principal_desc]

        # Create list of graphs to pass to Plotly        
        # Order = Cumulative Interest Income, Change in Interest Rates, Interest Rate, Remaining Balance, 
        graphs = [

            dict(
                data = [
                    dict(
                        x = am1['Period'],
                        y = am1['Interest Rate']*100,
                        type = 'scatter',
                        mode = 'lines',
                        name = 'Fixed with Reset'
                    ),
                    dict(
                        x = am1['Period'],
                        y = am2['Interest Rate']*100,
                        type = 'scatter',
                        mode = 'lines',
                        name = 'Fixed'
                    ),
                    dict(
                        x = am1['Period'],
                        y = am3['Interest Rate']*100,
                        type = 'scatter',
                        mode = 'lines',
                        name = 'Variable'
                    )
                ],
                layout = dict(
                        xaxis = dict(title = 'Payment Number'),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        yaxis = dict(title = 'Rate', zeroline = False, hoverformat = '.2f')
                    )

            ),
            dict(
                data = [
                    dict(
                        x = am1['Period'],
                        y = ii1,
                        type = 'scatter',
                        mode = 'lines',
                        name = 'Fixed with Reset'
                    ),
                    dict(
                        x = am1['Period'],
                        y = ii2,
                        type = 'scatter',
                        mode = 'lines',
                        name = 'Fixed'
                    ),
                    dict(
                        x = am1['Period'],
                        y = ii3,
                        type = 'scatter',
                        mode = 'lines',
                        name = 'Variable'
                    )
                ],
                layout = dict(
                        xaxis = dict(title = 'Payment Number', range = [0, am1['Period'].iloc[-1]+1]),
                        yaxis = dict(title = 'Amount', zeroline = False, hoverformat = ',.0f'),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                    )

            ),
            dict(
                data = [
                    dict(
                        x = am1['Period'],
                        y = am1['Payment'],
                        type = 'scatter',
                        mode = 'lines',
                        name = 'Fixed with Reset'
                    ),
                    dict(
                        x = am1['Period'],
                        y = am2['Payment'],
                        type = 'scatter',
                        mode = 'lines',
                        name = 'Fixed'
                    ),
                    dict(
                        x = am1['Period'],
                        y = am3['Payment'],
                        type = 'scatter',
                        mode = 'lines',
                        name = 'Variable'
                    )
                ],
                layout = dict(
                        xaxis = dict(title = 'Payment Number'),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        yaxis = dict(title = 'Amount', zeroline = False, hoverformat = ',.0f')
                    )

            ),
            dict(
                data = [
                    dict(
                        x = am1['Period'],
                        y = am1['Begin Balance'],
                        type = 'scatter',
                        mode = 'lines',
                        name = 'Fixed with Reset'
                    ),
                    dict(
                        x = am1['Period'],
                        y = am2['Begin Balance'],
                        type = 'scatter',
                        mode = 'lines',
                        name = 'Fixed'
                    ),
                    dict(
                        x = am1['Period'],
                        y = am3['Begin Balance'],
                        type = 'scatter',
                        mode = 'lines',
                        name = 'Variable'
                    )
                ],
                layout = dict(
                        xaxis = dict(title = 'Payment Number'),
                        yaxis = dict(title = 'Amount', zeroline = False, hoverformat = ',.0f'),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )

            ),
            dict(
                data = [
                    dict(
                        x = am1['Period'],
                        y = proxy_rates[:l1['term']+1],
                        fill='tozeroy'
                    )
                ],
                layout = dict(
                        xaxis = dict(title = 'Payment Number', range = [0, am1['Period'].iloc[-1]+1]),
                        yaxis = dict(title = '% Change', zeroline = False, tickformat=".2%",hoverformat = ',.3f'),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                    )

            )

        ]

        # Create IDs for the each graph
        ids = ['graph-{}'.format(i) for i, item in enumerate(graphs)]

        graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template("index.html", graphJSON = graphJSON, ids = ids, IRdict = IRdict, desc_list = desc_list)
    else:
        form = LoanForm()
        return render_template("index.html", form = form)

@app.route('/about')
def about():
    return render_template("about.html")

#def amort():

