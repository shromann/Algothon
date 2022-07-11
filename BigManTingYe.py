import pandas as pd
import numpy as np
from math import log, exp


nInst = 100

position = np.zeros(nInst, int)
long = {}
short = {}

mrWindow = 8
width = 1

TEN_K = 10000

holdings = np.array([{} for _ in range(nInst)])

def getMyPosition(price):
    global position

    position += delta(price)
    return position

def delta(price):
    # price: the price data given for this turn
    price = pd.DataFrame(price).T

    # currPrice: the current price, can buy or sell
    currPrice = price.iloc[-1]

    # posChange: the netChange we want to make to our current position 
    posChange = np.zeros(nInst, int)

    # days: days passed (incl today) thus far 
    days  = price.__len__()

    #=============================================== Statical Mean Reversion Strategy ===============================================#

    # don't trade prior to mrReversion window days
    if days < mrWindow + 1:
        return posChange
    
    LD = price.iloc[-mrWindow-1:].applymap(log).diff().dropna()
    LDHist = LD.iloc[:-1]

    MLD, SLD = LDHist.mean(), LDHist.std()
    LB, UB = MLD - (width * SLD), MLD + (width * SLD)
    lastPrice = price.iloc[-2]

    MLD = MLD.map(exp) * lastPrice
    LB = LB.map(exp)   * lastPrice
    UB = UB.map(exp)   * lastPrice

    # Run LDMR 
    posChange += MeanReversion(currPrice, MLD, LB, UB)
    

    # TODO: testing purposes (remove to run the whole thing)
    if days == 20:
        exit(1)


    return posChange



def MeanReversion(currPrice, MLD, LB, UB):
    """
    Simple Model
    """
    # open_trades
    def open_trades(currPrice, long, short):
        global position
        currWorth = position * currPrice
        buy, sell = ((TEN_K - currWorth[long]) / currPrice[long]).map(int), ((TEN_K + currWorth[short]) / currPrice[short]).map(int)
        
        position[long] += buy
        position[short] -= sell


        # update Open Holdings
        for i in buy.index:
            holdings[i].update({currPrice[i]:buy[i]})
        
        for i in sell.index:
            holdings[i].update({currPrice[i]:-sell[i]})

        return buy, sell
        
    # close_trades
    def close_trades(currPrice):
        global position
        global holdings
        
        newHoldings = [hold.copy() for hold in holdings]

        for i, hold in enumerate(holdings):
            for price, qty in hold.items():
                if (qty > 0 and currPrice[i] > price) or (qty < 0 and currPrice[i] < price):
                    position[i] -= qty
                    del newHoldings[i][price]
                else:
                    continue

        holdings = newHoldings



    posChange = np.zeros(nInst, int)
    
    long, short = currPrice < LB, currPrice > UB

    open_trades(currPrice, long, short)
    close_trades(currPrice)


    # ==== DEBUG ZONE


    # print(position)    

    i = 10
    print(holdings[i])
    print(position[i], currPrice[i])
    if currPrice[i] < LB[i]:
        print('buy')
    elif currPrice[i] > UB[i]:
        print('sell')
    else:
        print('hold')

    return posChange


