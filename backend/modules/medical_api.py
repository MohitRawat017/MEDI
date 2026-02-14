import requests


# -----------------------------
# RxNorm → Standard ID
# -----------------------------

def fetch_rxnorm_id(drug_name: str):
    url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}"
    r = requests.get(url)

    if r.status_code != 200:
        return None

    data = r.json()

    if "idGroup" in data and "rxnormId" in data["idGroup"]:
        return data["idGroup"]["rxnormId"][0]

    return None


# -----------------------------
# DailyMed → Drug Label Summary
# -----------------------------

def fetch_dailymed_summary(drug_name: str):
    url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name={drug_name}"
    r = requests.get(url)

    if r.status_code != 200:
        return None

    data = r.json()

    if "data" not in data or len(data["data"]) == 0:
        return None

    # Get first match
    spl = data["data"][0]

    return {
        "title": spl.get("title"),
        "setid": spl.get("setid"),
        "published_date": spl.get("published_date"),
    }
