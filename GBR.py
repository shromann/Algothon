# def delta(price):
#     global LogD

#     # 1. Create `price` DataFrame
#     price = pd.DataFrame(price).T
#     currPrice = price.iloc[-1]

#     # 2. Don't Trade if we don't have at least 4 days of Data, return same postion
#     if price.__len__() < 4:
#         return position

#     # 3. Create `D`: Log Difference in the prices for our ML training  
#     processLogD(price)

#     # 4. Predict Tomorrows price
#     preds = prediction(currPrice)

#     print(currPrice.iloc[0], preds[0])

#     # # 5. Create `pos`: a vector of length 100 saying how much we want to Long or Short today
#     # pos = np.zeros(nInst)

#     # # 6. close yesterday's trades (if any)
#     # pos += closeOld(currPrice, preds)

#     # # 7. open trades for tomorrow
#     # pos += openNew(currPrice, preds)
    
#     return position

# def processLogD(price):
#     global LogD
    
#     # 1. Creat LogD for the First Time
#     if LogD.__len__() == 0:
#         for s in price:
#             LogD[s] = logDiff(price[s])

#     else:
#         # 2. Just add the difference into the row
#         d = price.iloc[-2: ]
#         D = pd.DataFrame(columns=range(nInst))
#         for s in d:
#             D[s] = logDiff(d[s])

#         LogD = insert_row(LogD, D.T, 250)



# def prediction(currPrice):
#     global LogD
#     global day
#     global record

#     models = np.array([GradientBoostingRegressor() for _ in range(nInst)])

#     pred = []
#     for s, m in enumerate(models):
#         y = LogD[s]
#         X = LogD[[s, max_corr[s]]]        

#         X_train, y_train = X.iloc[:-2], y.iloc[1:-1]
#         X_test = [X.iloc[-1]]

#         m.fit(X_train, y_train)

#         pred.append(m.predict(X_test))
    
#     pred = pd.Series([exp(p[0] * prob[s] * conf[s]) * currPrice[s] for s, p in enumerate(pred)]).to_numpy()
#     record = insert_row(record, pred, 250)
#     record.to_csv('backtest1.csv', index=False)
#     return pred