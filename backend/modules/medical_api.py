import requests


# -----------------------------
# RxNorm → Standard ID
# -----------------------------

def fetch_rxnorm_id(drug_name: str):
    try:
        r = requests.get(
            "https://rxnav.nlm.nih.gov/REST/rxcui.json",
            params={"name": drug_name},
            timeout=10,
        )
        if r.status_code != 200:
            return None
        data = r.json()
    except (requests.RequestException, ValueError):
        return None

    if not isinstance(data, dict):
        return None

    if "idGroup" in data and "rxnormId" in data["idGroup"]:
        return data["idGroup"]["rxnormId"][0]

    return None


# -----------------------------
# DailyMed → Drug Label Summary
# -----------------------------

def fetch_dailymed_summary(drug_name: str):
    try:
        r = requests.get(
            "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json",
            params={"drug_name": drug_name},
            timeout=10,
        )
        if r.status_code != 200:
            return None
        data = r.json()
    except (requests.RequestException, ValueError):
        return None

    if not isinstance(data, dict) or not data.get("data"):
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
    try:
        r = requests.get(
            "https://rxnav.nlm.nih.gov/REST/rxclass/class/byDrugName.json",
            params={"drugName": drug_name, "relaSource": "ATC"},
            timeout=10,
        )
        if r.status_code != 200:
            return []

        data = r.json()
        if not isinstance(data, dict):
            return []

        classes = []

        concept_groups = data.get("rxclassDrugInfoList", {}).get("rxclassDrugInfo", [])
        for info in concept_groups:
            class_name = info.get("rxclassMinConceptItem", {}).get("className")
            if class_name and class_name not in classes:
                classes.append(class_name)

        return classes

    except (requests.RequestException, ValueError):
        return []


# -----------------------------
# OpenFDA → Adverse Events
# -----------------------------

def fetch_openfda_interactions(drug_name: str) -> list[str]:
    """
    Query OpenFDA drug adverse events for interaction-related reports.
    Returns list of reported interaction terms.
    """
    try:
        r = requests.get(
            "https://api.fda.gov/drug/event.json",
            params={
                "search": (
                    f'patient.drug.medicinalproduct:"{drug_name}"'
                    '+AND+patient.reaction.reactionmeddrapt:"drug interaction"'
                ),
                "limit": 5,
            },
            timeout=10,
        )
        if r.status_code != 200:
            return []

        data = r.json()
        if not isinstance(data, dict):
            return []

        results = data.get("results", [])
        interactions = []

        for result in results:
            drugs = result.get("patient", {}).get("drug", [])
            for drug in drugs:
                name = drug.get("medicinalproduct", "")
                if name and name.lower() != drug_name.lower() and name not in interactions:
                    interactions.append(name)

        return interactions

    except (requests.RequestException, ValueError):
        return []
