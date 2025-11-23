"""
Excel Utilities
Helper functions for reading and processing Excel files
"""
import pandas as pd
import re
import warnings
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import List, Dict, Any, Optional

# Suppress openpyxl warnings about unknown extensions
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')


class ExcelUtils:
    """Utility class for Excel operations"""
    
    @staticmethod
    def safe_read_excel(path: Path, sheet_name=None, header=0, engine="openpyxl"):
        """Read Excel file without locking"""
        with open(path, "rb") as f:
            return pd.read_excel(BytesIO(f.read()), sheet_name=sheet_name, header=header, dtype=str, engine=engine).fillna("")
    
    @staticmethod
    def safe_read_excel_sheetnames(path: Path, engine="openpyxl"):
        """Get Excel sheet names without locking"""
        with open(path, "rb") as f:
            xl = pd.ExcelFile(BytesIO(f.read()), engine=engine)
            names = xl.sheet_names
            xl.close()
            return names
    
    @staticmethod
    def try_parse_date(txt: str) -> Optional[datetime]:
        """Try to parse date from text"""
        txt = str(txt).strip()
        for fmt in ("%d.%m.%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%d-%b-%Y", "%d %b %Y"):
            try:
                return datetime.strptime(txt, fmt)
            except:
                continue
        return None
    
    @staticmethod
    def pick_latest_sheet(sheet_names: List[str], target_date=None) -> str:
        """Pick the latest sheet by date"""
        candidates = []
        for name in sheet_names:
            d = ExcelUtils.try_parse_date(name)
            if d:
                candidates.append((d, name))
        
        if not candidates:
            return sheet_names[-1]
        
        if target_date:
            matches = [x for x in candidates if x[0].date() == target_date]
            if matches:
                return matches[0][1]
        
        return max(candidates, key=lambda x: x[0])[1]
    
    @staticmethod
    def format_number(x) -> str:
        """Format number with commas"""
        if not x or x == "":
            return ""
        try:
            return f"{float(x):,.0f}"
        except:
            return str(x)
    
    @staticmethod
    def to_number(s) -> Optional[float]:
        """Convert string to number"""
        if not s:
            return None
        s = str(s).strip()
        neg = s.startswith("(") and s.endswith(")")
        if neg:
            s = s[1:-1]
        s_clean = re.sub(r'[^0-9\.]', '', s)
        try:
            return -float(s_clean) if neg else float(s_clean)
        except:
            return None
    
    @staticmethod
    def strike_key(s) -> Any:
        """Generate strike key"""
        if not s:
            return ""
        s_clean = re.sub(r'[^0-9]', '', str(s))
        return int(s_clean) if s_clean.isdigit() else str(s).upper()
    
    def extract_historical_table(self, hist_path: Path, stock: str) -> List[Dict[str, Any]]:
        """Extract historical data"""
        try:
            sheet_names = self.safe_read_excel_sheetnames(hist_path)
            sheet = self.pick_latest_sheet(sheet_names)
            df = self.safe_read_excel(hist_path, sheet_name=sheet)
            df.columns = [str(c).strip() for c in df.columns]
            
            stock_col = next((c for c in df.columns if re.search(r"stock|symbol|name", c, re.I)), None)
            if not stock_col:
                return []
            
            df["__clean"] = df[stock_col].str.upper().str.strip().apply(lambda x: re.sub(r'\W+', '', x))
            
            if stock.upper() not in df["__clean"].values:
                return []
            
            data = df[df["__clean"] == stock.upper()].copy()
            if data.empty:
                return []
            
            result = []
            for _, r in data.iterrows():
                row = {
                    col: str(r.get(col, "")) 
                    for col in ["Stock", "Category", "Strike", "Prev_OI", "Latest_OI", 
                               "Call_OI_Difference", "Put_OI_Difference", "LTP", "Additional_Strike"]
                }
                
                for k in ["Prev_OI", "Latest_OI", "Call_OI_Difference", "Put_OI_Difference"]:
                    row[k] = self.format_number(self.to_number(row[k]))
                
                row["Additional_Strike"] = str(row.get("Additional_Strike", "")).strip()
                result.append(row)
            
            return result
        except Exception as e:
            print(f"Historical error {stock}: {e}")
            return []
    
    def extract_live_table(self, live_path: Path, hist_path: Path, stock: str) -> List[Dict[str, Any]]:
        """Extract live data from Live.xlsx"""
        try:
            # First, get historical data for comparison
            sheet_names = self.safe_read_excel_sheetnames(hist_path)
            sheet1 = self.pick_latest_sheet(sheet_names)
            df1 = self.safe_read_excel(hist_path, sheet_name=sheet1)
            df1.columns = [str(c).strip() for c in df1.columns]
            
            stock_col = next((c for c in df1.columns if re.search(r"stock|symbol|name", c, re.I)), None)
            call_map, put_map, all_strikes = {}, {}, set()
            add_map = {}
            
            if stock_col:
                df1["__clean"] = df1[stock_col].str.upper().str.strip().apply(lambda x: re.sub(r'\W+', '', x))
                df1 = df1[df1["__clean"] == stock.upper()]
                
                for _, r in df1.iterrows():
                    k = self.strike_key(r.get("Strike", ""))
                    all_strikes.add(k)
                    v = self.to_number(r.get("Latest_OI", ""))
                    cat = str(r.get("Category", "")).lower()
                    
                    if "call" in cat and v is not None:
                        call_map[k] = v
                    if "put" in cat and v is not None:
                        put_map[k] = v
                    
                    raw_add = str(r.get("Additional_Strike", "")).strip()
                    if raw_add:
                        low = raw_add.lower()
                        if low in ("yes", "y", "1", "true"):
                            add_map[k] = "Yes"
                        else:
                            add_map[k] = raw_add
            
            # Read live data
            live_sheet_names = self.safe_read_excel_sheetnames(live_path)
            today = datetime.now().date()
            chosen = None
            dated = []
            
            for n in live_sheet_names:
                d = self.try_parse_date(n)
                if d:
                    dated.append((d, n))
                if d and d.date() == today:
                    chosen = n
                    break
            
            if not chosen:
                chosen = max(dated, key=lambda x: x[0])[1] if dated else live_sheet_names[-1]
            
            raw = self.safe_read_excel(live_path, sheet_name=chosen, header=None)
            texts = [" ".join([str(x).strip() for x in row if str(x).strip()]) for row in raw.values]
            
            stock_norm = re.sub(r'\W+', '', stock.upper())
            start_idx = self._find_live_block_start(texts, stock_norm)
            
            if start_idx is None:
                return []
            
            end_idx = next((j for j in range(start_idx + 1, len(texts))
                           if re.search(r'^\s*OPT[_\-\s]?[A-Za-z0-9]+', texts[j], re.I)), len(texts))
            
            block = raw.iloc[start_idx:end_idx].reset_index(drop=True)
            
            # Find sections
            sections = {}
            for i in range(len(block)):
                line = " ".join([str(x).strip() for x in block.iloc[i]])
                tl = line.lower()
                if 'call support' in tl:
                    sections['Call Support'] = i
                if 'put support' in tl:
                    sections['Put Support'] = i
                if 'call resistance' in tl:
                    sections['Call Resistance'] = i
                if 'put resistance' in tl:
                    sections['Put Resistance'] = i
            
            result = []
            for sec_name, sec_idx in sections.items():
                for r in range(sec_idx + 1, len(block)):
                    row_vals = [str(x).strip() for x in block.iloc[r]]
                    if all(v == "" for v in row_vals):
                        break
                    if any(h in " ".join(row_vals).lower() for h in 
                          ('call support', 'put support', 'call resistance', 'put resistance')):
                        break
                    if len(row_vals) < 10:
                        continue
                    
                    if "call" in sec_name.lower():
                        label, prev_oi, strike = row_vals[0], row_vals[1], row_vals[2]
                    else:
                        label, prev_oi, strike = row_vals[6], row_vals[7], row_vals[8]
                    
                    prev_num = self.to_number(prev_oi)
                    sk = self.strike_key(strike)
                    oi_diff = ""
                    
                    if prev_num is not None:
                        base = call_map.get(sk, 0) if "call" in sec_name.lower() else put_map.get(sk, 0)
                        oi_diff = self.format_number(prev_num - base)
                    
                    add_strike_value = add_map.get(sk, "")
                    
                    result.append({
                        "Section": sec_name,
                        "Label": label,
                        "Prev_OI": self.format_number(prev_num),
                        "Strike": strike,
                        "Stock": stock,
                        "OI_Diff": oi_diff,
                        "Is_NewStrike": "Yes" if sk not in all_strikes else "",
                        "Add_Strike": add_strike_value
                    })
            
            return result
        except Exception as e:
            print(f"Live error {stock}: {e}")
            return []
    
    @staticmethod
    def _find_live_block_start(texts: List[str], stock_norm: str) -> Optional[int]:
        """Find start of stock block in live data"""
        for i, line in enumerate(texts):
            if re.search(rf"OPT[_\-\s]*{re.escape(stock_norm)}", line, re.I):
                return i
        return None
