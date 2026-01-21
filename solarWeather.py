"""
    ** Developer **
    David Bower

    *** PURPOSE *** 
    This tool gathers the last two hours of solar weather
    reported from NOAA SWPC 

    Exports the data gathered from NOAA SWPC JSON files 
        - https://services.swpc.noaa.gov/json/goes/primary/
            X --> xray flares data? 
    
    Prints off the two hour timeline in cosonle, .csv, or .json

    ** Modification History **
    Initial Implementation - DAB 01/17/2026

    Scan the results, created if logic for solar flare cases. - DAB 01/20/2026

-------------------------------------------------------------------

    Astronomy Questions:

    X -> What is used to measure solar activity? 
        - Xray devices from NOAA 
        Soft Xray flux: 
            - Flares are split up in different classes
            A,B,C,M,X --> Power level ranging (10^-8 -> 10^-4)
            I believe this is called Soft X-Ray flux 

        Magnetic energy from sunspots, UV Radiation, Solar Magnetic fields, 
        and solar winds

        
    Dad wants this measure X-ray flux (W/m^2) over time? 

    What is this URL that leads to xrays-1-day.json? 
        This is a live feed from whats collected from NOAA's xray sensor.
        It is updated every minute 

"""



from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

## Import email requirements here 

import requests 

# DATA SOURCE --> I GET MEASUREMENTS FROM THIS JSON 
SRC_URL = "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json"

# These store the different classes of flares mentioned above
# Along with their power level. 
FLARE_OFFSETS = [
    ("A", 1e-8),
    ("B", 1e-7),
    ("C", 1e-6),
    ("M", 1e-5),
    ("X", 1e-4)
]

#print(f"This is the strongest: {type(FLARE_OFFSETS[4][1])}")
STRONG_FLARE = FLARE_OFFSETS[4][1]

# boolean comparison if flare is x
def is_x_flare(flux: float) -> bool:
    return flux >= STRONG_FLARE
# ALERT THE SCIENTIST
def x_flare_Alert(entries: list[xrayEntry]) -> None:
    if not entries:
        return
    
    # Find strongest flare
    strongest = max(entries, key=lambda e: e.flux)
    # No action if weaker 
    if not is_x_flare(strongest.flux):
        return

    if is_x_flare(strongest.flux):

        ## Insert email logic here 
        print("STRONG ASS FLARE DETECTED")

# HELPER FUNCTION TO DEFINE FLARE CLASS 
def flare_class(flux: float) -> str:
    if flux <= 0:
        return "A0.00"
    
    for flare, offset in FLARE_OFFSETS:
        if flux >= offset:
            return f"{offset}{(flux/offset):.2f}"
        
    return f"A{(flux / 1e-8):.2f}"


# This is a data structure for one measurement 
@dataclass(frozen=True)
class xrayEntry:
    time_utc: datetime
    flux: float # W/m^2 measurement 
    observed_flux: float 
    #contaminated: bool 


"""
    Download JSON data from NOAA
    RETURNS AS DATA
"""
def fetch_json(url: str, session: Optional[requests.Session] = None) -> list[dict[str, Any]]:

    s = session or requests.Session()

    r = s.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()

    if not isinstance(data, list):
        raise ValueError(f"Expected a list, got {type(data)}")
    
    print("NOAA : XRAYS-1-DAY JSON FETCHED")

    return data

"""
    This function goes through fetched JSON from NOAA
    Filters for energy values of 0.1-0.8nm
"""
def filter_data(rows: list[dict[str, Any]], energy: str = '0.1-0.8nm') -> list[dict[str, Any]]:
    #print(rows)
    return [i for i in rows if str(i.get("energy", "")).strip() == energy]

"""
    This function will assign each entry from the gathered CSV 
    to its own node from the data structure above. 

    Converts the raw data to data entries for organization
"""
def split_entries(data: list[dict[str, Any]], time_key: str = "time_tag", flux_key: str = "flux") -> list[xrayEntry]:
    entries: list[xrayEntry] = []
    for i in data:
        try:
            time = timeConvert(str(i["time_tag"]))
            flux = float(i["flux"])
            obs = float(i.get("observed_flux", flux))
        except Exception:
            continue
        
        # Append to the list
        entries.append(xrayEntry(time_utc=time, flux=flux, observed_flux=obs))

    entries.sort(key=lambda i: i.time_utc)
    return entries

# LEET CODE PROBLEM 
def getLastNHoras(entries: list[xrayEntry], hours: float) -> list[xrayEntry]:
    if not entries:
        return []
    # Last index
    end = entries[-1].time_utc

    #1print("DEBUG: ", end ,type(end)) --> Need parser 

    start = end - timedelta(hours=hours)
    return [i for i in entries if start <= i.time_utc <= end]

## SUMMARIZE & EXPORT 
def summary(entries: list[xrayEntry]) -> dict[str, Any]:
    if not entries:
        raise ValueError("No entries available.")
    
    curr = entries[-1].flux
    max_flux = max(i.flux for i in entries)
    return {
        "start_time_utc": entries[0].time_utc.isoformat(),
        "end_time_utc": entries[-1].time_utc.isoformat(),
        "Amount of nodes(measurements)": len(entries),
        "current_flux": curr,
        "current_class": flare_class(curr),
        "max_flux": flare_class(max_flux),
        "max_class": flare_class(max_flux),
    }

# SAVE AND WRITE FILE HELPERS ----------
def save_file(entries: list[xrayEntry], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("TIME(UTC),FLUX,OBSERVED_FLUX,FLARE_OFFSET,CONTAMINATED")
        for i in entries:
            f.write(
                f"{i.time_utc.isoformat()},"
                f"{i.flux:.10e},"
                f"{i.observed_flux:.10e},"
                f"{flare_class(i.flux)}\n"
                #f"{str(i.contaminated).lower()}\n"
            )
def write_file(payload: dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

# SAVE AND WRITE FILE HELPERS ---------- END 

# TIME STR -> DATETIME 
def timeConvert(time_stamp: str) -> datetime:
    if time_stamp.endswith("Z"):
        time_stamp = time_stamp[:-1] + "+00:00"

    date_time = datetime.fromisoformat(time_stamp)
    if date_time.tzinfo is None:
        date_time = date_time.replace(tzinfo=timezone.utc)
    return date_time.astimezone(timezone.utc)

# MAIN FUNCTION | WIRE THE FUNCTIONS TOGETHER 
if __name__ == "__main__":
    # Download from data source
    data = fetch_json(SRC_URL)

    # Filter for only nodes with energy: 0.1-0.8nm 
    data = filter_data(data, energy="0.1-0.8nm")

    if not data:
        raise RuntimeError("No energy value found for energy='0.1-0.8nm'")
    
    # PARSE TIME STAMPS 
    
    # Split the data into entry NODES 
    data = split_entries(data)


    # DAD WANTS THE LAST TWO HOURS. HE MONITORS: https://www.spaceweatherlive.com/en/solar-activity.html 
    # He may want to change it
    data2h = getLastNHoras(data, 2)

    ## SUMMARIZE AND EXPORT DATA FOR ANALYSIS
    dataSummary = summary(data2h)

    payload = {
        "Source_URL": SRC_URL,
        "energy": "0.1-0.8nm",
        "two hour summary": dataSummary,
        "entries_twoHour" : [
            {
                "time_utc": i.time_utc.isoformat(),
                "flux": i.flux,
                "observed_flux": i.observed_flux,
                "flare_class": flare_class(i.flux)
            }
            for i in data2h
        ],
    }

    print(json.dumps(dataSummary, indent=2))
    save_file(data2h, "solarWeather2h.csv")
    write_file(payload, "solarWeather2h.json")
    print("Wrote: csv file, json file")



