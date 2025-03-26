```
                           _ _ 
      _ ____ __ ___ _ __ _| | |
     | '_ \ V  V / '_/ _` | | |
     | .__/\_/\_/|_| \__,_|_|_|
     |_|                       
------------------------------------
       Power Ball Predictor
------------------------------------

====================================
              ABOUT
  -------------------------------

Pwrall (Power Ball Predictor) predicts Power Ball
draw by simulating computerized lottery drawing.


====================================
              LINKS
  -------------------------------

+ Kaggle: https://pwrall.com/kaggle

+ GitHub: https://pwrall.com/github


====================================
            HOW TO USE
  -------------------------------

#----------#

import json
import time
from datetime import datetime
from datetime import timedelta
import pandas as pd
import numpy as np
import os
import warnings 
warnings.filterwarnings('ignore')

PWRALL_DIR = "/kaggle/buffers/pwrall"

os.system(f'mkdir -p "{PWRALL_DIR}"')
os.system(f'cd "{PWRALL_DIR}" && git clone https://github.com/dinhtt-randrise/pwrall.git')

import sys 
sys.path.append(os.path.abspath(PWRALL_DIR))
import pwrall.pwrall as vpwrl

#----------#

BUY_DATE = '2025.03.23'
BUFFER_DIR = '/kaggle/buffers/pwrall'
DATA_DF = None
DATE_CNT = 56 * 5
O_DATE_CNT = 7
TCK_CNT = 56 * 5
RUNTIME = 60 * 60 * 11.5
PRD_SORT_ORDER = 'B'
HAS_STEP_LOG = True
RANGE_CNT = 52
M5P_OBS = True
M5P_CNT = 3
M5P_VRY = True
LOAD_CACHE_DIR = '/kaggle/working'
SAVE_CACHE_DIR = '/kaggle/working'

METHOD = 'simulate'
#METHOD = 'observe'
#METHOD = 'observe_range'
#METHOD = 'download'

#----------#

pwrl = vpwrl.PwrallSimulator(PRD_SORT_ORDER, HAS_STEP_LOG, M5P_OBS, M5P_CNT, M5P_VRY, LOAD_CACHE_DIR, SAVE_CACHE_DIR)

if METHOD == 'simulate':
    zdf, json_pred, pdf = pwrl.simulate(BUY_DATE, BUFFER_DIR, DATA_DF, DATE_CNT, TCK_CNT, RUNTIME)
    if zdf is not None:
        zdf.to_csv(f'/kaggle/working/pb-sim-{BUY_DATE}.csv', index=False)
    if pdf is not None:
        pdf.to_csv(f'/kaggle/working/pb-pick-{BUY_DATE}.csv', index=False)
    if json_pred is not None:
        json_pred['s_pred'] = pwrl.cn2sn(json_pred['pred'])
        json_pred['s_m5_pred'] = pwrl.cn2sn(json_pred['m5_pred'])
        with open(f'/kaggle/working/pb-pred-{BUY_DATE}.json', 'w') as f:
            json.dump(json_pred, f)

        text = '''
====================================
    PREDICT: [PB] __BD__
  -------------------------------

+ Predicted Numbers: __RS__

+ M5P Numbers: __M5__

+ Win Number:

+ Result: 

+ M5P Result:

+ Predict Notebook:


  -------------------------------
              MONEY
  -------------------------------

+ Period No: 

+ Day No: 

+ Tickets: 280

+ Cost: $364

+ Total Cost: $644

+ Prize: $0

+ Total Prize: $0

+ Current ROI: 0.0  


  -------------------------------
            REAL BUY
  -------------------------------

+ Buy Number: __M5__

+ Confirmation Number: 

+ Cost: $4.6

+ Total Cost: $4.6

+ Prize: $0

+ Total Prize: $0

+ Current ROI: 0.0

        '''
        text = text.replace('__BD__', str(BUY_DATE)).replace('__RS__', str(pwrl.cn2sn(json_pred['pred']))).replace('__M5__', str(pwrl.cn2sn(json_pred['m5_pred'])))
        with open(f'/kaggle/working/pb-pred-{BUY_DATE}.txt', 'w') as f:
            f.write(text)
        print(text)

if METHOD == 'observe':
    odf, more = pwrl.observe(BUY_DATE, TCK_CNT, O_DATE_CNT, RUNTIME, DATE_CNT, BUFFER_DIR, DATA_DF)

    if odf is not None and more is not None and len(odf) > 0:
        odf.to_csv(f'/kaggle/working/pb-observe-{BUY_DATE}.csv', index=False)
        qdf = odf[odf['m5'] > 0]
        if len(qdf) > 0:
            for ri in range(len(qdf)):
                t_buy_date = qdf['buy_date'].iloc[ri]

                key = 'pred_' + t_buy_date    
                if key in more:
                    json_pred = more[key]
                    if json_pred is not None:
                        json_pred['s_pred'] = pwrl.cn2sn(json_pred['pred'])
                        json_pred['s_m5_pred'] = pwrl.cn2sn(json_pred['m5_pred'])
                        with open(f'/kaggle/working/pb-pred-{t_buy_date}.json', 'w') as f:
                            json.dump(json_pred, f)

                key = 'sim_' + t_buy_date                
                if key in more:
                    xdf = more[key]
                    if xdf is not None:
                        xdf.to_csv(f'/kaggle/working/pb-sim-{t_buy_date}.csv', index=False)

                key = 'pick_' + t_buy_date                
                if key in more:
                    xdf = more[key]
                    if xdf is not None:
                        xdf.to_csv(f'/kaggle/working/pb-pick-{t_buy_date}.csv', index=False)

if METHOD == 'observe_range':
    v_draw_date = pwrl.previous(BUY_DATE)
    start_time = time.time()
    range_idx = 0
    while range_idx < RANGE_CNT:
        if time.time() - start_time > RUNTIME:
            break
            
        d1 = datetime.strptime(v_draw_date, "%Y.%m.%d")
        d2 = d1 + timedelta(minutes=int(+((60 * 24))))
        v_buy_date = d2.strftime('%Y.%m.%d')
        o_overtime = time.time() - start_time
        v_runtime = RUNTIME - o_overtime

        odf, more = pwrl.observe(v_buy_date, TCK_CNT, O_DATE_CNT, v_runtime, DATE_CNT, BUFFER_DIR, DATA_DF)

        if odf is not None and more is not None and len(odf) > 0:
            odf.to_csv(f'/kaggle/working/pb-observe-{v_buy_date}.csv', index=False)
            qdf = odf[odf['m5'] > 0]
            if len(qdf) > 0:
                for ri in range(len(qdf)):
                    t_buy_date = qdf['buy_date'].iloc[ri]
    
                    key = 'pred_' + t_buy_date    
                    if key in more:
                        json_pred = more[key]
                        if json_pred is not None:
                            json_pred['s_pred'] = pwrl.cn2sn(json_pred['pred'])
                            json_pred['s_m5_pred'] = pwrl.cn2sn(json_pred['m5_pred'])
                            with open(f'/kaggle/working/pb-pred-{t_buy_date}.json', 'w') as f:
                                json.dump(json_pred, f)
    
                    key = 'sim_' + t_buy_date                
                    if key in more:
                        xdf = more[key]
                        if xdf is not None:
                            xdf.to_csv(f'/kaggle/working/pb-sim-{t_buy_date}.csv', index=False)
    
                    key = 'pick_' + t_buy_date                
                    if key in more:
                        xdf = more[key]
                        if xdf is not None:
                            xdf.to_csv(f'/kaggle/working/pb-pick-{t_buy_date}.csv', index=False)

        v_draw_date = pwrl.previous_dow(v_draw_date)
        range_idx += 1

if METHOD == 'download':    
    data_df = pwrl.download_drawing(BUFFER_DIR, BUY_DATE)

    if data_df is not None:
        data_df.to_csv(f'/kaggle/working/pb-{BUY_DATE}.csv', index=False)

#----------#


====================================
             CACHES
  -------------------------------


  -------------------------------
         FORWARD CACHES
  -------------------------------

[ 2025.03.23 ]

+ Notebook: https://www.kaggle.com/code/dinhttrandrise/pwrall-cache-f-2025-03-23


  -------------------------------
         BACKWARD CACHES
  -------------------------------

[ 2025.03.23 ]

+ Notebook: 


```
