import re
import pandas as pd
dim_df = pd.read_csv("candidateEvalData/dim_df_correct.csv")
raw_data = dim_df['rawDim'].tolist()
pattern = '\d+\,?.?\d*\s*x?×?b?y?\s*\d*\,?.?\d*\s*x?×?b?y?\s*\d*\,?.?\d*\s*in|\d+\,?.?\d*\s*x?×?b?y?\s*\d*\,?.?\d*\s*x?×?b?y?\s*\d*\,?.?\d*\s*cm'
data_list = []
for raw in raw_data:
    all_chars = re.findall(pattern,raw)
    val = None
    for ac in all_chars:
        val = ac if 'cm' in ac else val
        prev = ac
        val = prev if val == None else val
    val = val.replace("cm", "").replace("in", "").replace(",", ".").strip()
    try:
        height = float(val.split("x")[0].strip() )if 'x' in val else (float(val.split("×")[0].strip()) if '×' in val else (float(val.split("by")[0].strip())*2.54 if 'by' in val else None))
    except Exception:
        height = None
        pass
    try:
        width = float(val.split("x")[1].strip()) if 'x' in val else (float(val.split("×")[1].strip()) if '×' in val else (float(val.split("by")[1].strip()) * 2.54 if 'by' in val else None))
    except Exception:
        width = None
        pass
    try:
        depth = float(val.split("x")[2].strip()) if 'x' in val else (float(val.split("×")[2].strip()) if '×' in val else (float(val.split("by")[2].strip()) * 2.54 if 'by' in val else None))
    except Exception:
        depth = None
        pass
    res = {
        'rawDim': raw,
        'height': height,
        'width': width,
        'depth': depth
    }
    data_list.append(res)
df = pd.DataFrame(data_list)
print(df)

