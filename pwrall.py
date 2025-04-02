# ------------------------------------------------------------ #
#                           _ _ 
#      _ ____ __ ___ _ __ _| | |
#     | '_ \ V  V / '_/ _` | | |
#     | .__/\_/\_/|_| \__,_|_|_|
#     |_|                       
#------------------------------------
#       Power Ball Predictor
#------------------------------------
#
#====================================
#            LINKS
#  -------------------------------
#
# + Kaggle: https://pwrall.com/kaggle
#
# + GitHub: https://pwrall.com/github
#
# + Lottery: https://pwrall.com/lotte
#
#
#====================================
#            Copyright
#  -------------------------------
#
# "Power Ball Predictor" is written and copyrighted
# by Dinh Thoai Tran <dinhtt@randrise.com> [https://dinhtt.randrise.com]
#
#
#====================================
#            License
#  -------------------------------
#
# "Power Ball Predictor" is distributed under Apache-2.0 license
# [ https://github.com/dinhtt-randrise/pwrall/blob/main/LICENSE ]
#
# ------------------------------------------------------------ #

import random
import os
import json
import time
from datetime import datetime
from datetime import timedelta
import pandas as pd
import numpy as np
import pickle

# ------------------------------------------------------------ #

class PwrallSimulator:
    def __init__(self, prd_sort_order = 'A', has_step_log = True, m5p_obs = False, m5p_cnt = -1, m5p_vry = True, load_cache_dir = '/kaggle/working', save_cache_dir = '/kaggle/working', heading_printed = False):
        self.lottery_dows = ['Monday', 'Wednesday', 'Saturday']
        
        self.min_num = 0
        self.max_num = (69 * 69 * 69 * 69 * 69) - 1
        
        self.baseset = {0: 69*69*69*69, 1: 69*69*69, 2: 69*69, 3: 69, 4: 1}

        self.heading_printed = heading_printed

        if prd_sort_order not in ['A', 'B', 'C']:
            prd_sort_order = 'A'
        self.prd_sort_order = prd_sort_order

        self.has_step_log = has_step_log
        self.m5p_obs = m5p_obs
        self.m5p_cnt = m5p_cnt

        if m5p_cnt < 2:
            m5p_vry = False
        self.m5p_vry = m5p_vry

        self.cache_capture_seed = {}
        self.cache_reproduce_one = {}
        self.cache_capture = {}

        self.debug_on = False
        self.debug_gn_on = False
        self.debug_cs_on = False

        os.system(f'mkdir -p "{load_cache_dir}"')
        self.load_cache_dir = load_cache_dir

        os.system(f'mkdir -p "{save_cache_dir}"')
        self.save_cache_dir = save_cache_dir

        self.load_cache()

    def save_cache(self):
        cdir = self.save_cache_dir

        fn = f'{cdir}/cache_capture_seed.pkl'
        with open(fn, 'wb') as f:
            pickle.dump(self.cache_capture_seed, f)

        fn = f'{cdir}/cache_reproduce_one.pkl'
        with open(fn, 'wb') as f:
            pickle.dump(self.cache_reproduce_one, f)

        fn = f'{cdir}/cache_capture.pkl'
        with open(fn, 'wb') as f:
            pickle.dump(self.cache_capture, f)

    def load_cache(self):
        cdir = self.load_cache_dir
        
        fn = f'{cdir}/cache_capture_seed.pkl'
        if os.path.exists(fn):
            with open(fn, 'rb') as f:
                self.cache_capture_seed = pickle.load(f)

        fn = f'{cdir}/cache_reproduce_one.pkl'
        if os.path.exists(fn):
            with open(fn, 'rb') as f:
                self.cache_reproduce_one = pickle.load(f)

        fn = f'{cdir}/cache_capture.pkl'
        if os.path.exists(fn):
            with open(fn, 'rb') as f:
                self.cache_capture = pickle.load(f)

    def print_heading(self):
        if self.heading_printed:
            return
        self.heading_printed = True
            
        text = '''
                           _ _ 
      _ ____ __ ___ _ __ _| | |
     | '_ \ V  V / '_/ _` | | |
     | .__/\_/\_/|_| \__,_|_|_|
     |_|                       
------------------------------------
       Power Ball Predictor
------------------------------------
        '''
        print(text)

    def next_dow(self, date):
        d1 = datetime.strptime(date, "%Y.%m.%d")
        g = 1
        d2 = d1 + timedelta(minutes=int(+(g*(60 * 24))))
        tag_dow = d2.strftime('%A')
        tag_date = d2.strftime('%Y.%m.%d') 
        max_cnt = 10
        cnt = 1
        while tag_dow not in self.lottery_dows and cnt <= max_cnt:
            cnt += 1
            g += 1
            d2 = d1 + timedelta(minutes=int(+(g*(60 * 24))))
            tag_dow = d2.strftime('%A')
            tag_date = d2.strftime('%Y.%m.%d') 
        return tag_date
      
    def previous_dow(self, date):
        d1 = datetime.strptime(date, "%Y.%m.%d")
        g = -1
        d2 = d1 + timedelta(minutes=int(+(g*(60 * 24))))
        tag_dow = d2.strftime('%A')
        tag_date = d2.strftime('%Y.%m.%d') 
        max_cnt = 10
        cnt = 1
        while tag_dow not in self.lottery_dows and cnt <= max_cnt:
            cnt += 1
            g -= 1
            d2 = d1 + timedelta(minutes=int(+(g*(60 * 24))))
            tag_dow = d2.strftime('%A')
            tag_date = d2.strftime('%Y.%m.%d') 
        return tag_date
        
    def gen_num(self):
        n = self.a2n(self.n2a(random.randint(self.min_num, self.max_num)))
        
        if self.debug_gn_on:
            print(f'=> [GN1] {n}')
            
        while n is None:
            n = self.a2n(self.n2a(random.randint(self.min_num, self.max_num)))
            
            if self.debug_gn_on:
                print(f'=> [GN2] {n}')

        if self.debug_gn_on:
            print(f'=> [GN3] {n}')
        self.debug_gn_on = False
        
        return n

    def capture_seed(self, sim_cnt, n):
        key = f'{sim_cnt}_{n}'
        if key in self.cache_capture_seed:
            return self.cache_capture_seed[key]
            
        sim_seed = 0
        p = self.reproduce_one(sim_seed, sim_cnt)

        if self.debug_cs_on:
            print(f'=> [CS1] {sim_seed}, {sim_cnt}, {n}, {p}')
            
        while not self.match(n, p):
            sim_seed += 1
            p = self.reproduce_one(sim_seed, sim_cnt)

            if self.debug_cs_on:
                if sim_seed % 100000 == 0:
                    print(f'=> [CS2] {sim_seed}, {sim_cnt}, {n}, {p}')

        if self.debug_cs_on:
            print(f'=> [CS3] {sim_seed}, {sim_cnt}, {n}, {p}')

        self.debug_cs_on = False

        self.cache_capture_seed[key] = sim_seed
        
        return sim_seed

    def capture(self, w, n):
        key = f'{w}_{n}'
        if key in self.cache_capture:
            return self.cache_capture[key][0], self.cache_capture[key][1]
            
        if self.debug_on:
            print(f'=> [C1] {w}, {n}')
            
        sim_seed = self.capture_seed(1, n)

        if self.debug_on:
            print(f'=> [C2] {sim_seed}, {w}, {n}')

        random.seed(sim_seed)
        
        sim_cnt = 0
        p = self.gen_num()
        sim_cnt += 1

        if self.debug_on:
            print(f'=> [C3] {sim_seed}, {sim_cnt}, {w}, {n}')

        while not self.match(w, p, 'm5'):
            p = self.gen_num()
            sim_cnt += 1

            if self.debug_on:
                if sim_cnt % 100000 == 0:
                    print(f'=> [C4] {sim_seed}, {sim_cnt}, {w}, {n}')

        pn = self.reproduce_one(sim_seed, 1)
        pw = self.reproduce_one(sim_seed, sim_cnt)

        if self.debug_on:
            print(f'=> [C5] {sim_seed}, {sim_cnt}, {w}, {n}, {pw}, {pn}')

        self.debug_on = False
        
        if pn == n and pw == w:
            self.cache_capture[key] = [sim_seed, sim_cnt]
            return sim_seed, sim_cnt
        else:
            self.cache_capture[key] = [-1, -1]
            return -1, -1
            
    def reproduce_one(self, sim_seed, sim_cnt):
        key = f'{sim_seed}_{sim_cnt}'
        if key in self.cache_reproduce_one:
            return self.cache_reproduce_one[key]
            
        random.seed(sim_seed)
        n = -1
        for si in range(sim_cnt):
            n = self.gen_num()

        self.cache_reproduce_one[key] = n
        
        return n

    def match_count(self, w, n):
        wa = self.n2a(w)
        na = self.n2a(n)
        if wa is None or na is None:
            return 0
            
        cnt = 0
        for n in na:
            if n in wa:
                cnt += 1
        return cnt
        
    def match(self, w, p, match_kind = 'm5'):
        if match_kind == 'm5':
            if w < 0:
                return False
            elif w == p:
                return True
            else:
                return False
        elif match_kind == 'm4':
            cnt = self.match_count(w, p)
            if w < 0:
                return False
            elif cnt >= 4:
                return True
            else:
                return False
        elif match_kind == 'm3':
            cnt = self.match_count(w, p)
            if w < 0:
                return False
            elif cnt >= 4:
                return True
            else:
                return False
        else:
            return False

    def a2n(self, a):
        if a is None:
            return None
        if len(a) < 5:
            return None

        b = [x for x in a]
        b.sort()
        
        n = 0
        for ni in range(5):
            n += (b[ni] - 1) * self.baseset[ni]
        return n
    
    def n2a(self, n):
        try:
            if n is None:
                return None

            a = []
            for ni in range(5):
                b = self.baseset[ni]
                c = int((n - (n % b)) // b)
                if c + 1 in a:
                    return None
                a.append(c + 1)
                n = n - (c * b)
            a.sort()
            
            return a
        except Exception as e:
            return None

    def download_drawing(self, buffer_dir, v_date):
        self.print_heading()

        text = '''
====================================
        DOWNLOAD DRAWING
  -------------------------------
        '''
        print(text) 

        text = '''
  -------------------------------
           PARAMETERS
  -------------------------------
        '''
        print(text) 

        v_date = self.previous_dow(v_date)
        
        print(f'[BUFFER_DIR] {buffer_dir}')
        print(f'[DATE] {v_date}')

        text = '''
  -------------------------------
        '''
        print(text) 

        tmp_dir = buffer_dir
        work_dir = f'{tmp_dir}/data-' + str(random.randint(1, 1000000))  
        os.system(f'mkdir -p {work_dir}')

        curl_file = f'{work_dir}/curl.txt'
        fds = v_date.split('.')
        END_DATE = str(int(fds[1])) + '/' + str(int(fds[2])) + '/' + str(int(fds[0]))[2:]
        cmd = "curl 'https://api2.oregonlottery.org/drawresults/ByDrawDate?gameSelector=pb&startingDate=01/01/1984&endingDate=" + END_DATE + "&pageSize=50000&includeOpen=False' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Accept-Language: en-US,en;q=0.9' -H 'Cache-Control: no-cache' -H 'Connection: keep-alive' -H 'Ocp-Apim-Subscription-Key: 683ab88d339c4b22b2b276e3c2713809' -H 'Origin: https://www.oregonlottery.org' -H 'Pragma: no-cache' -H 'Referer: https://www.oregonlottery.org/' -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-site' -H 'User-Agent: Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36' -H 'sec-ch-ua: " + '"' + "Not/A)Brand" + '"' + ";v=" + '"' + "8" + '"' + ", " + '"' + "Chromium" + '"' + ";v=" + '"' + "126" + '"' + ", " + '"' + "Google Chrome" + '"' + ";v=" + '"' + "126" + '"' + "' -H 'sec-ch-ua-mobile: ?0' -H 'sec-ch-ua-platform: " + '"' + "Chrome OS" + '"' + "' > " + curl_file
        print(cmd)
        os.system(cmd)
            
        FIND = v_date.replace('.', '-') + 'T19:00:00'
        data = []
        if os.path.exists(curl_file):
            with open(curl_file, 'r') as f:
                data = json.load(f)
        line = ''
        for di in range(len(data)):
            et = data[di]
            if et['DrawDateTime'] == FIND:
                line = 'yes'
                break
        
        if line == '':
            os.system(f'rm -rf {work_dir}')
            print(f'== [Error] ==> Drawing is not found!')
            return None

        rows = []
        for di in range(len(data)):
            et = data[di]
            date = et['DrawDateTime'].split('T')[0].replace('-', '.')  
            sl = et['WinningNumbers']
            sl = sl[:5]
            n = self.a2n(sl)
            if n is None:
                continue
            rw = {'date': date, 'w': -1, 'n': n}
            rows.append(rw)
        ddf = pd.DataFrame(rows)    

        rows = []
        date_list = ddf['date'].unique()
        for today in date_list:
            d1 = datetime.strptime(today, "%Y.%m.%d")
            d2 = d1 + timedelta(minutes=int(+(1) * (60 * 24)))
            buy_date = d2.strftime('%Y.%m.%d')   
            next_date = self.next_dow(today)
            tdf = ddf[ddf['date'] == today]
            bdf = ddf[ddf['date'] == next_date]
            n = tdf['n'].iloc[0]
            ns = str(self.n2a(n))
            ws = ''
            if len(bdf) == 0:
                w = -1
            else:
                w = bdf['n'].iloc[0]
                ws = str(self.n2a(w))
            rw = {'date': today, 'buy_date': buy_date, 'next_date': next_date, 'w': w, 'n': n, 'ws': ws, 'ns': ns}
            rows.append(rw)
        df = pd.DataFrame(rows)
        df = df.sort_values(by=['date'], ascending=[False])
        os.system(f'rm -rf {work_dir}')

        sz = len(df)
        print(f'== [Success] ==> Drawing data is downloaded. It contains {sz} rows.')
        
        text = '''
  -------------------------------
        DOWNLOAD DRAWING
====================================
        '''
        print(text) 

        return df
        
    def simulate(self, v_buy_date, buffer_dir = '/kaggle/buffers/pwrall', data_df = None, v_date_cnt = 56, tck_cnt = 2, runtime = None):
        self.print_heading()

        pso = self.prd_sort_order
        if pso == 'C':
            tck_cnt = -1
            pso = 'B'
            
        text = '''
====================================
       ANALYZE SIMULATION
  -------------------------------
        '''
        print(text) 

        text = '''
  -------------------------------
           PARAMETERS
  -------------------------------
        '''
        print(text) 

        v_data_df_is_none = False
        if data_df is None:
            v_data_df_is_none = True

        v_draw_date = self.previous_dow(v_buy_date)
        d1 = datetime.strptime(v_draw_date, "%Y.%m.%d")
        d2 = d1 + timedelta(minutes=int(+(1) * (60 * 24)))
        v_buy_date = d2.strftime('%Y.%m.%d')  
        v_draw_date = self.next_dow(v_draw_date)
        
        print(f'[BUFFER_DIR] {buffer_dir}')
        print(f'[DATA_DF_IS_NONE] {v_data_df_is_none}')
        print(f'[DRAW_DATE] {v_draw_date}')
        print(f'[BUY_DATE] {v_buy_date}')
        print(f'[DATE_CNT] {v_date_cnt}')
        print(f'[TCK_CNT] {tck_cnt}')
        print(f'[RUNTIME] {runtime}')

        text = '''
  -------------------------------
        '''
        print(text) 

        if data_df is None:
            data_df = self.download_drawing(buffer_dir, v_buy_date)
            if data_df is None:
                return None, None, None
                
        rwcnt = v_date_cnt * 2 + 1
        start_time = time.time()
        ddf = data_df[data_df['buy_date'] <= v_buy_date]
        ddf = ddf.sort_values(by=['buy_date'], ascending=[False])
        if v_date_cnt > 0:
            if len(ddf) > rwcnt:
                ddf = ddf[:rwcnt]
        ddf = ddf.sort_values(by=['buy_date'], ascending=[True])
        rows = []
        sz = len(ddf)
        db_cnt = int(round(sz / 100.0))
        if db_cnt <= 0:
            db_cnt = 1
        m5_cnt = 0
        m4_cnt = 0
        m3_cnt = 0
        for ri in range(len(ddf)):
            if runtime is not None:
                if time.time() - start_time > runtime:
                    break
            if self.has_step_log:
                if ri % db_cnt == 0:
                    print(f'== [S1] ==> {ri} / {sz}')
                
            t_date = ddf['date'].iloc[ri]
            t_buy_date = ddf['buy_date'].iloc[ri]
            t_next_date = ddf['next_date'].iloc[ri]
            t_n = ddf['n'].iloc[ri]
            t_w = ddf['w'].iloc[ri]
            sim_seed = -1
            sim_cnt = -1
            t_p = -1
            m5 = 0
            m4 = 0
            m3 = 0
            a_m5 =0
            a_m4 = 0
            a_m3 = 0
            p_buy_date_m5 = ''
            p_sim_seed_m5 = ''
            p_win_num_m5 = ''
            p_prd_num_m5 = ''
            p_buy_date_m4 = ''
            p_sim_seed_m4 = ''
            p_win_num_m4 = ''
            p_prd_num_m4 = ''
            p_buy_date_m3 = ''
            p_sim_seed_m3 = ''
            p_win_num_m3 = ''
            p_prd_num_m3 = ''
            if t_w >= 0 and t_buy_date != v_buy_date:
                sim_seed, sim_cnt = self.capture(t_w, t_n)
                t_p = self.reproduce_one(sim_seed, sim_cnt)

                pdf = pd.DataFrame(rows)
                if len(pdf) >= v_date_cnt:
                    pdf = pdf.sort_values(by=['date'], ascending=[False])
                    pdf = pdf[:v_date_cnt]
                    for pi in range(len(pdf)):
                        p_sim_cnt = pdf['sim_cnt'].iloc[pi]
                        p_date = pdf['date'].iloc[pi]
                        p_q = self.reproduce_one(sim_seed, p_sim_cnt)
                        i_m5 = pdf['m5'].iloc[pi]
                        i_m4 = pdf['m4'].iloc[pi]
                        i_m3 = pdf['m3'].iloc[pi]
                        
                        pi_buy_date_m5 = pdf['p_buy_date_m5'].iloc[pi]
                        pi_sim_seed_m5 = pdf['p_sim_seed_m5'].iloc[pi]
                        pi_win_num_m5 = pdf['p_win_num_m5'].iloc[pi]
                        pi_prd_num_m5 = pdf['p_prd_num_m5'].iloc[pi]
                        pi_buy_date_m4 = pdf['p_buy_date_m4'].iloc[pi]
                        pi_sim_seed_m4 = pdf['p_sim_seed_m4'].iloc[pi]
                        pi_win_num_m4 = pdf['p_win_num_m4'].iloc[pi]
                        pi_prd_num_m4 = pdf['p_prd_num_m4'].iloc[pi]
                        pi_buy_date_m3 = pdf['p_buy_date_m3'].iloc[pi]
                        pi_sim_seed_m3 = pdf['p_sim_seed_m3'].iloc[pi]
                        pi_win_num_m3 = pdf['p_win_num_m3'].iloc[pi]
                        pi_prd_num_m3 = pdf['p_prd_num_m3'].iloc[pi]

                        if self.match(t_w, p_q, 'm5'):
                            a_m5 += 1
                            i_m5 += 1
                            if pi_buy_date_m5 != '':
                                pi_buy_date_m5 += ', ' 
                                pi_sim_seed_m5 += ', '
                                pi_win_num_m5 += ', '
                                pi_prd_num_m5 += ', '
                            pi_buy_date_m5 += str(t_buy_date)
                            pi_sim_seed_m5 += str(sim_seed)
                            pi_win_num_m5 += str(t_w)
                            pi_prd_num_m5 += str(p_q)

                        if self.match(t_w, p_q, 'm4'):
                            a_m4 += 1
                            i_m4 += 1
                            if pi_buy_date_m4 != '':
                                pi_buy_date_m4 += ', ' 
                                pi_sim_seed_m4 += ', '
                                pi_win_num_m4 += ', '
                                pi_prd_num_m4 += ', '
                            pi_buy_date_m4 += str(t_buy_date)
                            pi_sim_seed_m4 += str(sim_seed)
                            pi_win_num_m4 += str(t_w)
                            pi_prd_num_m4 += str(p_q)
                                
                        if self.match(t_w, p_q, 'm3'):
                            a_m3f += 1
                            i_m3f += 1
                            if pi_buy_date_m3 != '':
                                pi_buy_date_m3 += ', ' 
                                pi_sim_seed_m3 += ', '
                                pi_win_num_m3 += ', '
                                pi_prd_num_m3 += ', '
                            pi_buy_date_m3 += str(t_buy_date)
                            pi_sim_seed_m3 += str(sim_seed)
                            pi_win_num_m3 += str(t_w)
                            pi_prd_num_m3 += str(p_q)
                            
                        for xi in range(len(rows)):
                            if rows[xi]['date'] == p_date:
                                rows[xi]['m5'] = i_m5
                                rows[xi]['m4'] = i_m4
                                rows[xi]['m3'] = i_m3

                                rows[xi]['p_buy_date_m5'] = pi_buy_date_m5
                                rows[xi]['p_sim_seed_m5'] = pi_sim_seed_m5
                                rows[xi]['p_win_num_m5'] = pi_win_num_m5
                                rows[xi]['p_prd_num_m5'] = pi_prd_num_m5

                                rows[xi]['p_buy_date_m4'] = pi_buy_date_m4
                                rows[xi]['p_sim_seed_m4'] = pi_sim_seed_m4
                                rows[xi]['p_win_num_m4'] = pi_win_num_m4
                                rows[xi]['p_prd_num_m4'] = pi_prd_num_m4

                                rows[xi]['p_buy_date_m3'] = pi_buy_date_m3
                                rows[xi]['p_sim_seed_m3'] = pi_sim_seed_m3
                                rows[xi]['p_win_num_m3'] = pi_win_num_m3
                                rows[xi]['p_prd_num_m3'] = pi_prd_num_m3

                    m5_cnt += a_m5
                    m4_cnt += a_m4
                    m3_cnt += a_m3
                    
            else:
                sim_seed = self.capture_seed(1, t_n)
            rw = {'date': t_date, 'buy_date': t_buy_date, 'next_date': t_next_date, 'w': t_w, 'n': t_n, 'p': t_p, 'sim_seed': sim_seed, 'sim_cnt': sim_cnt, 'm5': m5, 'm4': m4, 'm3': m3, 'a_m5': a_m5, 'a_m4': a_m4, 'a_m3': a_m3, 'm5_cnt': m5_cnt, 'm4_cnt': m4_cnt, 'm3_cnt': m3_cnt, 'p_buy_date_m5': p_buy_date_m5, 'p_sim_seed_m5': p_sim_seed_m5, 'p_win_num_m5': p_win_num_m5, 'p_prd_num_m5': p_prd_num_m5      , 'p_buy_date_m4': p_buy_date_m4, 'p_sim_seed_m4': p_sim_seed_m4, 'p_win_num_m4': p_win_num_m4, 'p_prd_num_m4': p_prd_num_m4      , 'p_buy_date_m3': p_buy_date_m3, 'p_sim_seed_m3': p_sim_seed_m3, 'p_win_num_m3': p_win_num_m3, 'p_prd_num_m3': p_prd_num_m3}
            rows.append(rw)
        zdf = pd.DataFrame(rows)
        xdf = zdf[zdf['buy_date'] == v_buy_date]
        pdf = zdf[zdf['buy_date'] < v_buy_date]
        kdf = pdf.sort_values(by=['buy_date'], ascending=[False])
        json_pred = None
        m5_rsi = -1
        m5_pred = ''
        m5pc = 0
        if len(xdf) == 1 and len(pdf) >= v_date_cnt:
            s_sim_cnt = ''
            s_pred = ''
            if pso == 'A':
                pdf = pdf[(pdf['m5'] > 0)|(pdf['m4'] > 0)|(pdf['m3'] > 0)]
            mb_m5 = 0
            mb_m4 = 0
            mb_m3 = 0
            if len(pdf) > 0:
                if pso == 'A':
                    pdf = pdf.sort_values(by=['m5', 'm4', 'm3', 'date'], ascending=[False, False, False, False])
                if pso == 'B':
                    pdf = pdf.sort_values(by=['date'], ascending=[False])

                if tck_cnt > 0 and len(pdf) > tck_cnt:
                    pdf = pdf[:tck_cnt]
                l_sim_cnt = list(pdf['sim_cnt'].values)
                ls_sim_cnt = [str(x) for x in l_sim_cnt]
                s_sim_cnt = ', '.join(ls_sim_cnt)
                l_pred = []
                x_sim_seed = xdf['sim_seed'].iloc[0]
                for x_sim_cnt in l_sim_cnt:
                    x = self.reproduce_one(x_sim_seed, x_sim_cnt)
                    l_pred.append(x)
                zrsi = 0
                zrsiw = int(xdf['w'].iloc[0])
                for zp in l_pred:
                    if zp == zrsiw:
                        break
                    zrsi += 1
                if zrsi < len(l_pred):
                    m5_rsi = zrsi
                ls_pred = [str(x) for x in l_pred]
                s_pred = ', '.join(ls_pred)
                for pi in range(len(pdf)):
                    sv_sim_seed = ', ' + str(x_sim_seed) + ','

                    txt = ', ' + pdf['p_sim_seed_m5'].iloc[pi] + ','
                    if sv_sim_seed in txt:
                        mb_m5 = 1

                    txt = ', ' + pdf['p_sim_seed_m4'].iloc[pi] + ','
                    if sv_sim_seed in txt:
                        mb_m4 = 1
                                        
                    txt = ', ' + pdf['p_sim_seed_m3'].iloc[pi] + ','
                    if sv_sim_seed in txt:
                        mb_m3 = 1                    
            else:
                pdf = None
            if len(kdf) > 0 and len(xdf) > 0:
                kdf = kdf[kdf['m5'] > 0]
                if len(kdf) > 0:
                    kdf = kdf.sort_values(by=['buy_date'], ascending=[False])
                    m5p_cnt = self.m5p_cnt
                    if m5p_cnt > 0:
                        if len(kdf) > m5p_cnt:
                            kdf = kdf[:m5p_cnt]
                    lx_pred = []
                    x_sim_seed = xdf['sim_seed'].iloc[0]
                    for xi in range(len(kdf)):
                        x = self.reproduce_one(x_sim_seed, kdf['sim_cnt'].iloc[xi])
                        lx_pred.append(str(x))
                    m4_pred = ', '.join(lx_pred)
            json_pred = {'date': xdf['date'].iloc[0], 'buy_date': xdf['buy_date'].iloc[0], 'next_date': xdf['next_date'].iloc[0], 'w': int(xdf['w'].iloc[0]), 'n': int(xdf['n'].iloc[0]), 'sim_seed': int(xdf['sim_seed'].iloc[0]), 'date_cnt': v_date_cnt, 'tck_cnt': tck_cnt, 'sim_cnt': s_sim_cnt, 'pred': s_pred, 'm5_rsi': m5_rsi, 'm5_pred': m5_pred, 'm5pc': m5pc, 'pcnt': 1, 'm5': int(xdf['a_m5'].iloc[0]), 'm4': int(xdf['a_m4'].iloc[0]), 'm3': int(xdf['a_m3'].iloc[0]), 'm5_cnt': int(xdf['m5_cnt'].iloc[0]), 'm4_cnt': int(xdf['m4_cnt'].iloc[0]), 'm3_cnt': int(xdf['m3_cnt'].iloc[0]), 'mb_m5': mb_m5, 'mb_m4': mb_m4, 'mb_m3': mb_m3}
        else:
            pdf = None
            
        if json_pred is not None:
            text = '''
  -------------------------------
           PREDICTION
  -------------------------------
        '''
            print(text)
            print(str(json_pred))


        text = '''
  -------------------------------
       ANALYZE SIMULATION
====================================
        '''
        print(text)

        try:
            self.save_cache()
        except Exception as e:
            msg = str(e)
            print(f'=> [E] {msg}')
        
        return zdf, json_pred, pdf

    def cn2sn(self, cn):
        acn = cn.split(', ')
        asn = []
        for icn in acn:
            icn = int(icn)
            na = self.n2a(icn)
            if na is None:
                continue
            asn.append(str(na))
        return ' ; '.join(asn)
        
    def observe(self, v_buy_date, o_max_tck = 2, o_date_cnt = 56, o_runtime = 60 * 60 * 11.5, date_cnt = 56, buffer_dir = '/kaggle/buffers/pwrall', data_df = None):
        self.print_heading()

        start_time = time.time()

        more = {}
        
        text = '''
====================================
             OBSERVE
  -------------------------------
        '''
        print(text)

        text = '''
  -------------------------------
           PARAMETERS
  -------------------------------
        '''
        print(text) 

        v_data_df_is_none = False
        if data_df is None:
            v_data_df_is_none = True

        v_draw_date = self.previous_dow(v_buy_date)
        d1 = datetime.strptime(v_draw_date, "%Y.%m.%d")
        d2 = d1 + timedelta(minutes=int(+(1) * (60 * 24)))
        v_buy_date = d2.strftime('%Y.%m.%d')  
        v_draw_date = self.next_dow(v_draw_date)

        print(f'[BUFFER_DIR] {buffer_dir}')
        print(f'[DATA_DF_IS_NONE] {v_data_df_is_none}')
        print(f'[BUY_DATE] {v_buy_date}')
        print(f'[DATE_CNT] {date_cnt}')
        print(f'[O_DATE_CNT] {o_date_cnt}')
        print(f'[TCK_CNT] {o_max_tck}')
        print(f'[RUNTIME] {o_runtime}')

        text = '''
  -------------------------------
        '''
        print(text) 

        if data_df is None:
            data_df = self.download_drawing(buffer_dir, v_buy_date)
            
        if data_df is None:
            return None, more

        ddf = data_df[data_df['buy_date'] < v_buy_date]
        ddf = ddf.sort_values(by=['buy_date'], ascending=[False])
        ddf = ddf[:o_date_cnt]
        ddf = ddf.sort_values(by=['buy_date'], ascending=[True])

        tck_cnt = 0
        pcnt = 0
        m4_cnt = 0
        m3f_cnt = 0
        m3l_cnt = 0
        m3_cnt = 0
        m2_cnt = 0
        rows = []
        for ri in range(len(ddf)):
            if o_runtime is not None:
                if time.time() - start_time > o_runtime:
                    break
                
            t_date = ddf['date'].iloc[ri]
            t_buy_date = ddf['buy_date'].iloc[ri]
            t_next_date = ddf['next_date'].iloc[ri]
            t_w = ddf['w'].iloc[ri]
            t_n = ddf['n'].iloc[ri]

            text = '''
  -------------------------------
  [O] __DATE__ : __W__
  -------------------------------
        '''
            print(text.replace('__DATE__', str(t_buy_date)).replace('__W__', str(t_w))) 

            runtime = None
            if o_runtime is not None:
                o_overtime = time.time() - start_time
                runtime = o_runtime - o_overtime
            zdf, json_prd, pdf = self.simulate(t_buy_date, buffer_dir, lotte_kind, data_df, date_cnt, o_max_tck, runtime)
            more[f'pred_{t_buy_date}'] = json_prd
            more[f'sim_{t_buy_date}'] = zdf
            more[f'pick_{t_buy_date}'] = pdf
            
            t_pred = json_prd['pred']
            vry = True
            if self.m5p_obs:
                t_pred = json_prd['m5_pred']
                if self.m5p_vry:
                    if len(t_pred.split(', ')) != 1:
                        vry = False
            t_prd_lst = t_pred.split(', ')
            if o_max_tck > 0:
                if len(t_prd_lst) > o_max_tck:
                    t_prd_lst = t_prd_lst[:o_max_tck]
            nlst = [int(x) for x in t_prd_lst]
            pcnt += 1
            prd_num = len(nlst)
            tck_cnt += prd_num
            m5 = 0
            m4 = 0
            m3 = 0
            for t_p in nlst:
                if vry and self.match(t_w, t_p, 'm5'):
                    m5 += 1
                if vry and self.match(t_w, t_p, 'm4'):
                    m4 += 1
                if vry and self.match(t_w, t_p, 'm3'):
                    m3 += 1
            m5_cnt += m5
            m4_cnt += m4
            m3_cnt += m3

            rw = json_prd
            rw['m5'] = m5
            rw['m4'] = m4
            rw['m3'] = m3
            rw['m5_cnt'] = m5_cnt
            rw['m4_cnt'] = m4_cnt
            rw['m3_cnt'] = m3_cnt
            rw['pcnt'] = pcnt
            
            rows.append(rw)

            print(str(rw))

        odf = pd.DataFrame(rows)
        odf = odf.sort_values(by=['buy_date'], ascending=[False])
        
        text = '''
  -------------------------------
             OBSERVE
====================================
        '''
        print(text)

        return odf, more

    def build_cache(self, v_buy_date, cache_cnt = -1, buffer_dir = '/kaggle/buffers/pwrall', data_df = None, runtime = None):
        self.print_heading()
            
        text = '''
====================================
            BUILD CACHE
  -------------------------------
        '''
        print(text) 

        text = '''
  -------------------------------
           PARAMETERS
  -------------------------------
        '''
        print(text) 

        v_data_df_is_none = False
        if data_df is None:
            v_data_df_is_none = True

        v_draw_date = self.previous_dow(v_buy_date)
        d1 = datetime.strptime(v_draw_date, "%Y.%m.%d")
        d2 = d1 + timedelta(minutes=int(+(1) * (60 * 24)))
        v_buy_date = d2.strftime('%Y.%m.%d')  
        v_draw_date = self.next_dow(v_draw_date)
        
        print(f'[BUFFER_DIR] {buffer_dir}')
        print(f'[DATA_DF_IS_NONE] {v_data_df_is_none}')
        print(f'[DRAW_DATE] {v_draw_date}')
        print(f'[BUY_DATE] {v_buy_date}')
        print(f'[CACHE_CNT] {cache_cnt}')
        print(f'[RUNTIME] {runtime}')

        text = '''
  -------------------------------
        '''
        print(text) 

        if data_df is None:
            data_df = self.download_drawing(buffer_dir, v_buy_date)
            if data_df is None:
                return None
                
        start_time = time.time()
        ddf = data_df[data_df['buy_date'] <= v_buy_date]
        ddf = ddf[ddf['w'] >= 0]
        ddf = ddf.sort_values(by=['buy_date'], ascending=[False])
        if cache_cnt > 0:
            if len(ddf) > cache_cnt:
                ddf = ddf[:cache_cnt]
        ddf = ddf.sort_values(by=['buy_date'], ascending=[False])

        rows = []
        keycheck = {}
        sz = len(ddf)
        for ri in range(len(ddf)):
            if runtime is not None:
                if time.time() - start_time > runtime:
                    break
                    
            w = ddf['w'].iloc[ri]
            n = ddf['n'].iloc[ri]
            date = ddf['date'].iloc[ri]
            sim_seed, sim_cnt = self.capture(w, n)
            p = self.reproduce_one(sim_seed, sim_cnt)

            if ri % 50 == 0:
                print(f'=> [BC1] {date} : {ri} / {sz} -> {w}, {n} -> {sim_seed}, {sim_cnt} -> {p}')

            rw = {'date': date, 'w': w, 'n': n, 'sim_seed': sim_seed, 'sim_cnt': sim_cnt}
            rows.append(rw)
            
            if ri % 1000 == 0:
                try:
                    self.save_cache()
                except Exception as e:
                    msg = str(e)
                    print(f'=> [E] {msg}')
                    
        cdf = pd.DataFrame(rows)
        cdf = cdf.sort_values(by=['date'], ascending=[True])
        sz = len(cdf) * len(cdf)
        li = 0
        for ria in range(len(cdf)):
            if runtime is not None:
                if time.time() - start_time > runtime:
                    break
                    
            sim_seed = cdf['sim_seed'].iloc[ria]
            date_1 = cdf['date'].iloc[ria]
            w = cdf['w'].iloc[ria]
            n = cdf['n'].iloc[ria]
            for rib in range(len(cdf)):
                if runtime is not None:
                    if time.time() - start_time > runtime:
                        break
                        
                if rib >= ria:
                    break
                    
                date_2 = cdf['date'].iloc[rib]
                sim_cnt = cdf['sim_cnt'].iloc[rib]
                p = self.reproduce_one(sim_seed, sim_cnt)
                li += 1
                if li % 1000 == 0:
                    print(f'=> [BC2] {date_1}, {date_2} : {li} / {sz} -> {w}, {n} -> {sim_seed}, {sim_cnt} -> {p}')
                
        try:
            self.save_cache()
        except Exception as e:
            msg = str(e)
            print(f'=> [E] {msg}')
        
        rows = []
        for key in self.cache_capture.keys():
            fds = key.split('_')
            w = int(fds[0])
            n = int(fds[1])
            fds = self.cache_capture[key]
            sim_seed = fds[0]
            sim_cnt = fds[1]
            df = ddf[(ddf['w'] == w)&(ddf['n'] == n)]
            if len(df) == 0:
                continue
            date = df['date'].iloc[0]
            buy_date = df['buy_date'].iloc[0]
            next_date = df['next_date'].iloc[0]
            rw = {'date': date, 'buy_date': buy_date, 'next_date': next_date, 'w': w, 'n': n, 'sim_seed': sim_seed, 'sim_cnt': sim_cnt}
            rows.append(rw)

        if len(rows) == 0:
            return None
            
        cdf = pd.DataFrame(rows)
        cdf = cdf.sort_values(by=['buy_date'], ascending=[False])

        text = '''
  -------------------------------
            BUILD CACHE
====================================
        '''
        print(text)

        return cdf
        
# ------------------------------------------------------------ #
