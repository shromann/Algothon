import pandas as pd
import numpy as np
from math import log, exp


nInst = 100

position = np.zeros(nInst, int)


mrWindow = 9
width = 1

TEN_K = 10000
comm = 0.0025

holdings = np.array([{} for _ in range(nInst)])

moveRange = {k:(0, 0) for k in range(nInst)}

def getMyPosition(price):
    global position
    delta(price)
    return position

def delta(price):
    # price: the price data given for this turn
    price = pd.DataFrame(price).T

    # currPrice: the current price, can buy or sell
    currPrice = price.iloc[-1]

    # days: days passed (incl today) thus far 
    days  = price.__len__()

    #=============================================== Statical Mean Reversion Strategy ===============================================#

    # don't trade prior to mrReversion window days
    if days < mrWindow + 1:
        return
    
    LD = price.iloc[-mrWindow-1:].applymap(log).diff().dropna()
    LDHist = LD.iloc[:-1]

    MLD, SLD = LDHist.mean(), LDHist.std()
    LB, UB = MLD - (width * SLD), MLD + (width * SLD)
    lastPrice = price.iloc[-2]

    # Run LDMR 
    MeanReversion(currPrice, lastPrice, MLD, LB, UB)
    

    # TODO: testing purposes (remove to run the whole thing)
    # if days == 200:
    #     exit(1)


def MeanReversion(currPrice, lastPrice, MLD, LB, UB):
    """
    Simple Model
    """
    global moveRange
    global position
    
    LBP = LB.map(exp)   * lastPrice
    UBP = UB.map(exp)   * lastPrice

    realizedMove = currPrice.map(log) - lastPrice.map(log)
    moveRange = {k:(min(moveRange[k][0], realizedMove[k]), max(moveRange[k][1], realizedMove[k])) for k in range(nInst)}
    reversion = ((2 * MLD) - realizedMove).map(exp)
    
    moveRangeDf = pd.DataFrame(moveRange).applymap(exp).T
    optOpenValue = abs(((TEN_K) / abs(moveRangeDf[1] - moveRangeDf[0])) * (reversion - 1))
    

    def open_trades(currPrice, long, short):
        global position
        currWorth = position * currPrice
                    
        buySpace, sellSpace = TEN_K - currWorth[long], TEN_K + currWorth[short]
        
        buy = (pd.concat([optOpenValue[long], buySpace]).min() / currPrice[long]).map(int)
        sell = (pd.concat([optOpenValue[short], sellSpace]).min() / currPrice[short]).map(int)
                
        position[long] += buy
        position[short] -= sell

        for i in buy.index:
            holdings[i].update({currPrice[i]:buy[i]})
        
        for i in sell.index:
            holdings[i].update({currPrice[i]:-sell[i]})

    # close_trades
    def close_trades(currPrice):
        global position
        global holdings
        
        newHoldings = [hold.copy() for hold in holdings]        

        for i, hold in enumerate(holdings):
            for price, qty in hold.items():
                if (qty > 0 and (currPrice[i] * (1 - comm)) > (price * (1 + comm))) or (qty < 0 and (currPrice[i] * (1 + comm)) < (price * (1 - comm))):
                    position[i] -= qty
                    del newHoldings[i][price]
                else:
                    continue


        holdings = newHoldings

    longBoundary, shortBoundary = (1 + comm) / (1 - comm), (1 - comm) / (1 + comm)
    
    long, short = (currPrice < LBP) & (reversion > longBoundary), (currPrice > UBP) & (reversion < shortBoundary)


    close_trades(currPrice)
    open_trades(currPrice, long, short)

