"""MC2-P1: Market simulator."""

import pandas as pd
import numpy as np
import datetime as dt
import os
from util import get_data, plot_data

def compute_portvals(orders_file = "./orders/orders.csv", start_val = 1000000):

    data1=pd.read_csv(orders_file, index_col="Date")
    
    
    def get_p(data):
        data=data.sort_index()
        if '2011-06-15' in data.index:
            data=data.drop(['2011-06-15'])
        sd=data.ix[0].name
        ed=data.ix[-1].name
        dates = pd.date_range(sd, ed)
        syms=set(data.ix[:,0])
        syms=list(syms)
        prices=get_data(syms, dates)
        prices=prices.sort_index()
        prices.fillna(method="ffill", inplace=True)
        prices.fillna(method="bfill", inplace=True)
        prices['cash']=1
        
        trades=prices.copy()
        trades[:]=0
        
        dateIx=pd.to_datetime(data.index.tolist())
        i=0
        while i<data.shape[0]:
            order_type=data.ix[i,1]
            stock_type=data.ix[i,0]
            if order_type=='BUY':
                trades.ix[dateIx[i],stock_type]=trades.ix[dateIx[i],stock_type]+data.ix[i,2]
                trades.ix[dateIx[i], 'cash']=trades.ix[dateIx[i], 'cash']-(data.ix[i,2]*prices.ix[dateIx[i],stock_type]) 
            else:
                trades.ix[dateIx[i],stock_type]=trades.ix[dateIx[i],stock_type]-data.ix[i,2]
                trades.ix[dateIx[i], 'cash']=trades.ix[dateIx[i], 'cash']+(data.ix[i,2]*prices.ix[dateIx[i],stock_type])
            i=i+1        
        
        holdings=trades.copy()
        holdings.ix[0,'cash']=1000000+holdings.ix[0,'cash']
        
        i=1
        while i<holdings.shape[0]:
            holdings.ix[i,:]=holdings.ix[i-1,:]+holdings.ix[i,:]
            i=i+1
           
        portvals=np.sum(prices*holdings, axis=1)
        portvals=pd.Series.to_frame(portvals)
        portvals.columns=['portvals']
        ph=holdings*prices
        return portvals, ph

    def get_leverage(ph):
        Leverage=np.sum(abs(ph[1].ix[:,:-1]), axis=1)/np.sum(ph[1], axis=1)
        return Leverage
    
    ph=get_p(data1)
    leverage=get_leverage(ph)
    
    
    while len(set(leverage>3))>1:
        index_to_remove=pd.to_datetime(leverage[leverage>3].index[0])
        IR=index_to_remove.date()
        IR=str(IR)
        data=data1.drop(IR)
        ph=get_p(data)
        leverage=get_leverage(ph)
        
    return ph[0]