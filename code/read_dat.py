import fnmatch

import numpy as np
import pandas as pd
import xarray as xr

def is_float(s):
    try: 
        float(s)
    except ValueError:
        return False
    else:
        return True
    
def safe_to_float(vec):
    print(vec)
    try: 
        return vec.astype(float)
    except ValueError:
        return vec


def load(filename="ascii/ftk240412-20240419-0900_L2.dat"):

    with open(filename) as fh:
        linelist = []
        instrumentlist = [linelist,]
        for line in fh:
            if line == "\n":
                    linelist = []
                    instrumentlist.append(linelist)
                    continue
            line = line.split("\t")
            linelist.append(line[:-1])

    dflist = []
    for inst in instrumentlist[1:]:
        if len(inst) == 0:
            continue
        head = [line.split(" ")[0] for line in inst[0]]
        post = ["_"+col if is_float(col) else "" 
                     for col in inst[1]]
        names = [h+p for h,p in zip(head,post)]
        #header = instrumentlist[4][0]
        data = np.array(inst[2:])
        dfdict = {}
        df = pd.DataFrame({hed:safe_to_float(vec) for hed,vec in zip(names, data.T)})
        dflist.append(df)
    return dflist

def parse_time(df):
    datestr = df["DATETAG"].astype("int").astype("str")
    timestr =  df["TIMETAG2"]
    mstr =  ((df["TIMER"]-df["TIMER"].astype(int))*1e6).astype(int).astype(str)
    dtm = pd.to_datetime(datestr + timestr + mstr, format="%Y%j%H:%M:%S%f")
    return dtm

def add_time_index(df):
    df.set_index(pd.DatetimeIndex(parse_time(df)), inplace=True)
    df.sort_index(inplace=True)
    return df

def add_pres(df, mpr, mpr_keylist=["Pres", "TILT", "ABS_TILT"]):
    df = add_time_index(df)
    mpr = add_time_index(mpr)
    return pd.merge_asof(df, mpr[mpr_keylist], left_index=True, right_index=True)
  
def resample(df, dt="1s"):
    hdlist = fnmatch.filter(df.keys(), '*_???.??')
    return df[hdlist + ["Pres"]].resample(dt).mean().interpolate()



def merge(dflist, dt="1s"):
    dfed = resample(add_pres(dflist[0], dflist[3]), dt)
    dfeu = resample(add_pres(dflist[1], dflist[3]), dt)
    dflu = resample(add_pres(dflist[2], dflist[3]), dt)

    tmin = np.max([dflu.index.min(), dfed.index.min(), dfeu.index.min()])
    tmax = np.min([dflu.index.max(), dfed.index.max(), dfeu.index.max()])
    dfed = dfed[(dfed.index>=tmin) & (dfed.index<=tmax)]
    dfeu = dfeu[(dfeu.index>=tmin) & (dfeu.index<=tmax)]
    dflu = dflu[(dflu.index>=tmin) & (dflu.index<=tmax)]
    return dict(ed=dfed, lu=dflu, eu=dfeu)


def to_xarray(dflist):
    dfdict = merge(dflist)
    hdlist = fnmatch.filter(dfdict["ed"].keys(), '*_???.??')
    wvlist = [float(key.split("_")[1]) for key in hdlist]
    ds = xr.Dataset({"ed":(("time", "wavelength"), dfdict["ed"].iloc[:,:-1]),
                     "eu":(("time", "wavelength"), dfdict["eu"].iloc[:,:-1]),
                     "lu":(("time", "wavelength"), dfdict["lu"].iloc[:,:-1]),
                     "depth":(("time"), dfdict["ed"].iloc[:,-1])},
                     coords={"time":dfdict["ed"].index, 
                             "wavelength":wvlist})
    return ds

# dsd = ds.groupby(ds.depth).mean()




"""        for line in fh:
            if " : " in line:
                mlist = (line.split(" : "))
                attrs[mlist[0]] = mlist[1][:-1]
            elif ("INTTIME" in line) or (counter > 0):
                counter += 1
                vec = np.array(line[:-1].split())
                try:
                    vec[:4].astype(float)
                except ValueError:
                    print(vec)
                    continue
                #print(vec)
                if counter == 16:
                    counter = 0
    """