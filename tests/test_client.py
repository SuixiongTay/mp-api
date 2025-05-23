import os
import warnings

import pytest

from mp_api.client import MPRester
from mp_api.client.routes.materials import TaskRester, ProvenanceRester

# -- Rester name data for generic tests

key_only_resters = {
    "materials_phonon": "mp-11703",
    "materials_similarity": "mp-149",
    "doi": "mp-149",
    "materials_wulff": "mp-149",
    "materials_charge_density": "mp-1936745",
    "materials_provenance": "mp-149",
    "materials_robocrys": "mp-1025395",
}

search_only_resters = [
    "materials_grain_boundaries",
    "materials_electronic_structure_bandstructure",
    "materials_electronic_structure_dos",
    "materials_substrates",
    "materials_synthesis",
    "materials_similarity",
]

special_resters = ["materials_charge_density", "doi"]

ignore_generic = [
    "_user_settings",
    "_general_store",
    "_messages",
    # "tasks",
    # "bonds",
    "materials_xas",
    "materials_elasticity",
    "materials_fermi",
    "materials_alloys",
    # "summary",
]  # temp


mpr = MPRester()

# Temporarily ignore molecules resters while molecules query operators are changed
resters_to_test = [
    rester for rester in mpr._all_resters if "molecule" not in rester.suffix
]


@pytest.mark.skipif(os.getenv("MP_API_KEY") is None, reason="No API key found.")
@pytest.mark.parametrize("rester", resters_to_test)
def test_generic_get_methods(rester):
    # -- Test generic search and get_data_by_id methods
    name = rester.suffix.replace("/", "_")

    rester = rester(
        endpoint=mpr.endpoint,
        include_user_agent=True,
        session=mpr.session,
        # Disable monty decode on nested data which may give errors
        monty_decode=rester not in [TaskRester, ProvenanceRester],
        use_document_model=True,
    )

    if name not in ignore_generic:
        key = rester.primary_key
        if name not in key_only_resters:
            if key not in rester.available_fields:
                key = rester.available_fields[0]

            doc = rester._query_resource_data({"_limit": 1}, fields=[key])[0]
            assert isinstance(doc, rester.document_model)

            if name not in search_only_resters:
                doc = rester.get_data_by_id(doc.model_dump()[key], fields=[key])
                assert isinstance(doc, rester.document_model)

        elif name not in special_resters:
            doc = rester.get_data_by_id(key_only_resters[name], fields=[key])
            assert isinstance(doc, rester.document_model)
