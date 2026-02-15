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


# -----------------------------
# RxClass → Drug Classes
# -----------------------------

def fetch_drug_classes(drug_name: str) -> list[str]:
    """
    Fetch pharmacological classes for a drug via RxClass API.
    Returns list of class names (e.g., ["Anticoagulants", "Vitamin K Antagonists"]).
    """
    url = (
        f"https://rxnav.nlm.nih.gov/REST/rxclass/class/byDrugName.json"
        f"?drugName={drug_name}&relaSource=ATC"
    )

    try:
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return []

        data = r.json()
        classes = []

        concept_groups = data.get("rxclassDrugInfoList", {}).get("rxclassDrugInfo", [])
        for info in concept_groups:
            class_name = info.get("rxclassMinConceptItem", {}).get("className")
            if class_name and class_name not in classes:
                classes.append(class_name)

        return classes

    except Exception:
        return []


# -----------------------------
# OpenFDA → Adverse Events
# -----------------------------

def fetch_openfda_interactions(drug_name: str) -> list[str]:
    """
    Query OpenFDA drug adverse events for interaction-related reports.
    Returns list of reported interaction terms.
    """
    url = (
        f"https://api.fda.gov/drug/event.json"
        f"?search=patient.drug.medicinalproduct:\"{drug_name}\""
        f"+AND+patient.reaction.reactionmeddrapt:\"drug interaction\""
        f"&limit=5"
    )

    try:
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return []

        data = r.json()
        results = data.get("results", [])
        interactions = []

        for result in results:
            drugs = result.get("patient", {}).get("drug", [])
            for drug in drugs:
                name = drug.get("medicinalproduct", "")
                if name and name.lower() != drug_name.lower() and name not in interactions:
                    interactions.append(name)

        return interactions

    except Exception:
        return []
