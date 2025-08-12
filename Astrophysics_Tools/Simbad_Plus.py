from typing_extensions import Self
from packaging import version
import Astrophysics_Tools.Tools as Tools
import astroquery
from astroquery.simbad import SimbadClass
from astropy import table
import logging
from typing import Optional
'''
Basic Simbad functionality with Default votable fields added
Added functionality to get observations of a target with an instrument and the filters a target was observed in
'''
class Simbad_Plus(SimbadClass):
    _instances = {}
    def __new__(cls, target: str, *args, **kwargs) -> Self:
        additional_votable_fields = sorted(kwargs.get("additional_votable_fields", []))
        additional_votable_fields_str = ", ".join(additional_votable_fields) if additional_votable_fields else ""
        if (target, additional_votable_fields_str) in cls._instances:
            warning = f"This Simbad_Plus instance already exists: {target=}, {additional_votable_fields_str=}"
            logging.warning(warning)
            return cls._instances[(target, additional_votable_fields_str)]
        instance = super().__new__(cls)
        cls._instances[(target, additional_votable_fields_str)] = instance
        return instance

    def __init__(self, target: str, additional_votable_fields: Optional[list[str]] = None) -> None:
        super().__init__()
        is_old_key_names = version.parse(astroquery.__version__) < version.parse("0.4.9")
        if is_old_key_names:
            votable_fields_to_add = ["SPTYPE"]
        else:
            votable_fields_to_add = ["sp_type", "plx_value","F444W","pmra","pmra_prec","pmdec","pmdec_prec",]

        if additional_votable_fields is None:
            additional_votable_fields = []
        self.add_votable_fields(*votable_fields_to_add, *additional_votable_fields)
        self.votable_fields = self.get_votable_fields()
        self.target_name = target
        self.obs_table = self.get_observations()
        self.filters = self.get_observed_filters()
        return None


    def get_observations(self, instrument: str ="ALL") -> table.Table:
        if instrument.upper() == "ALL" and hasattr(self, 'obs_table'):
            return self.obs_table
        # could just filter the table... but this works aswell...
        return Tools.get_observations(target_name=self.target_name, instrument=instrument)


    def get_observed_filters(self, instrument: str ="ALL") -> list[str]:
        if instrument.upper() == "ALL" and hasattr(self, 'filters'):
            return self.filters
        return Tools.get_observed_filters_from_mast(target_name=self.target_name, instrument=instrument)

    def get_query(self) -> table.Table:
        if not hasattr(self, 'query'):
            self.query = super().query_object(self.target_name)
        return self.query #type: ignore

    def update_query(self, additional_votable_fields: list[str]) -> None:
        for field in additional_votable_fields:
            if field not in self.votable_fields:
                self.add_votable_fields(field)

        self.votable_fields = self.get_votable_fields()
        self.query = super().query_object(self.target_name)
        return None

    def __str__(self):
        information_text= f"Simbad_Plus Object:\n\
            target: {self.target_name},\n\
            votable_fields: {self.votable_fields},\n\
            Filters: {self.filters},\n\
            over {len(self.obs_table)} observations)"
        print(self.obs_table)
        return information_text
