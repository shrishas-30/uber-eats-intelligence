"""Generate reproducible synthetic Uber Eats capstone data for Days 1–3."""
from pathlib import Path
import numpy as np
import pandas as pd
SEED=42
CITIES=["Bengaluru","Mumbai","Hyderabad","Pune","Chennai"]
CATEGORIES=["Indian","Pizza","Burgers","Chinese","Healthy","Desserts","Mexican"]
POS=["Great food and quick delivery","Fresh and tasty, arrived on time","Excellent packaging and friendly service","Loved the meal, would order again","Delicious food and good value","Warm food and helpful delivery"]
NEU=["The food was okay and delivery was average","Average experience, nothing special","Order was fine, but could be better","Taste and delivery were acceptable"]
NEG=["Delivery was late and the food was cold","Missing items and poor packaging","Food arrived late and was not fresh","Incorrect order and disappointing service","Long preparation time and poor communication","The meal was cold and disappointing"]
def main():
    rng=np.random.default_rng(SEED); root=Path(__file__).resolve().parents[1]; out=root/'data'/'raw'; out.mkdir(parents=True,exist_ok=True)
    nc,nr,nd,no=2000,100,500,10000
    customers=pd.DataFrame({'customer_id':np.arange(1,nc+1),'age':rng.integers(18,71,nc),'gender':rng.choice(['Female','Male','Non-binary','Prefer not to say'],nc,p=[.46,.46,.03,.05]),'city':rng.choice(CITIES,nc),'signup_date':pd.Timestamp('2022-01-01')+pd.to_timedelta(rng.integers(0,1700,nc),unit='D'),'membership_type':rng.choice(['Standard','Plus','Premium'],nc,p=[.60,.30,.10])})
    restaurants=pd.DataFrame({'restaurant_id':np.arange(1,nr+1),'restaurant_name':[f'{rng.choice(["Urban","Golden","Spice","Fresh","Little","Royal"])} {rng.choice(CATEGORIES)} {i:03d}' for i in range(1,nr+1)],'restaurant_category':rng.choice(CATEGORIES,nr),'restaurant_rating':np.round(np.clip(rng.normal(3.9,.55,nr),2.2,5),2),'average_preparation_time':np.round(np.clip(rng.normal(26,7,nr),10,50),1),'city':rng.choice(CITIES,nr)})
    drivers=pd.DataFrame({'driver_id':np.arange(1,nd+1),'driver_rating':np.round(np.clip(rng.normal(4.2,.4,nd),2.5,5),2),'vehicle_type':rng.choice(['Bicycle','Scooter','Motorcycle'],nd,p=[.12,.48,.40]),'experience_years':np.round(rng.uniform(0,10,nd),1),'city':rng.choice(CITIES,nd)})
    times=pd.Timestamp('2025-01-01')+pd.to_timedelta(rng.integers(0,365*24*60,no),unit='m'); amounts=np.round(np.clip(rng.gamma(3,180,no)+100,120,2500),2); status=rng.choice(['Completed','Cancelled'],no,p=[.91,.09])
    orders=pd.DataFrame({'order_id':np.arange(100001,100001+no),'customer_id':rng.integers(1,nc+1,no),'restaurant_id':rng.integers(1,nr+1,no),'order_timestamp':times,'order_amount':amounts,'number_of_items':rng.integers(1,9,no),'order_status':status,'payment_method':rng.choice(['Card','UPI','Cash','Wallet'],no,p=[.28,.48,.12,.12])})
    eligible=orders[orders.order_status.eq('Completed')].copy(); pool=eligible.loc[rng.random(len(eligible))<.97].copy(); n=len(pool); distance=np.round(np.clip(rng.gamma(2.2,2.1,n),.5,20),2); traffic=rng.choice(['Low','Medium','High'],n,p=[.30,.48,.22]); weather=rng.choice(['Clear','Rain','Windy'],n,p=[.70,.20,.10]); prep=np.clip(rng.normal(26,7,n),8,55); tadd=pd.Series(traffic).map({'Low':0,'Medium':6,'High':13}).to_numpy(); wadd=pd.Series(weather).map({'Clear':0,'Rain':8,'Windy':3}).to_numpy(); dtime=np.clip(12+distance*4.2+tadd+wadd+rng.normal(0,5,n),12,110)
    deliveries=pd.DataFrame({'delivery_id':np.arange(500001,500001+n),'order_id':pool.order_id.to_numpy(),'driver_id':rng.integers(1,nd+1,n),'delivery_distance_km':distance,'delivery_time_minutes':np.round(dtime,1),'preparation_time_minutes':np.round(prep,1),'traffic_condition':traffic,'weather_condition':weather,'tip_amount':np.round(np.clip(pool.order_amount.to_numpy()*rng.uniform(.02,.12,n),0,250),2),'delivery_status':'Completed'})
    review_pool=pool.merge(deliveries[['order_id','delivery_time_minutes']],on='order_id'); review_pool=review_pool.loc[rng.random(len(review_pool))<.68].reset_index(drop=True); texts=[]; labels=[]; ratings=[]
    for row in review_pool.itertuples():
        late=row.delivery_time_minutes>55; ppos=.60-(.15 if late else 0); pneg=.16+(.22 if late else 0); lab=rng.choice(['Positive','Neutral','Negative'],p=[ppos,1-ppos-pneg,pneg]); labels.append(lab)
        if lab=='Positive': texts.append(rng.choice(POS)); ratings.append(int(rng.choice([4,5],p=[.35,.65])))
        elif lab=='Neutral': texts.append(rng.choice(NEU)); ratings.append(int(rng.choice([3,4],p=[.75,.25])))
        else: texts.append(rng.choice(NEG)); ratings.append(int(rng.choice([1,2,3],p=[.45,.40,.15])))
    reviews=pd.DataFrame({'review_id':np.arange(700001,700001+len(review_pool)),'order_id':review_pool.order_id,'customer_id':review_pool.customer_id,'restaurant_id':review_pool.restaurant_id,'review_text':texts,'rating':ratings,'sentiment_label':labels,'review_timestamp':review_pool.order_timestamp+pd.to_timedelta(rng.integers(1,72,len(review_pool)),unit='h')})
    paystatus=np.where(orders.order_status.eq('Cancelled'),rng.choice(['Refunded','Paid'],no,p=[.88,.12]),'Paid')
    payments=pd.DataFrame({'payment_id':np.arange(900001,900001+no),'order_id':orders.order_id,'payment_method':orders.payment_method,'payment_amount':orders.order_amount,'payment_status':paystatus,'payment_timestamp':orders.order_timestamp+pd.to_timedelta(rng.integers(0,20,no),unit='m')})
    tables={'customers':customers,'restaurants':restaurants,'drivers':drivers,'orders':orders,'deliveries':deliveries,'reviews':reviews,'payments':payments}
    for name,df in tables.items(): df.to_csv(out/f'{name}.csv',index=False); print(f'{name}.csv: {df.shape}')
    assert customers.customer_id.is_unique and restaurants.restaurant_id.is_unique and drivers.driver_id.is_unique and orders.order_id.is_unique
    assert orders.customer_id.isin(customers.customer_id).all() and orders.restaurant_id.isin(restaurants.restaurant_id).all()
    assert deliveries.order_id.isin(eligible.order_id).all() and deliveries.driver_id.isin(drivers.driver_id).all()
    assert reviews.order_id.isin(orders.order_id).all() and payments.order_id.isin(orders.order_id).all()
    check=reviews.merge(orders[['order_id','customer_id','restaurant_id']],on='order_id',suffixes=('_review','_order'))
    assert check.customer_id_review.eq(check.customer_id_order).all() and check.restaurant_id_review.eq(check.restaurant_id_order).all()
    print('All critical key and relationship checks passed.')
    print('Review sentiment proportions:'); print(reviews.sentiment_label.value_counts(normalize=True).round(3))
if __name__=='__main__': main()
