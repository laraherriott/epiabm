#
# Calculate household force of infection based on Covidsim code
#

from pyEpiabm.core import Parameters
import pyEpiabm.core

from .personal_foi import PersonalInfection


class HouseholdInfection:
    """Class to calculate the infectiousness and susceptibility
    parameters for the force of infection parameter, within households.

    """
    @staticmethod
    def household_inf(infector, time: float):
        """Calculate the infectiousness of a person in a given
        household. Does not include interventions such as isolation,
        or whether individual is a carehome resident.

        Parameters
        ----------
        infector : Person
            Infector
        time : float
            Current simulation time

        Returns
        -------
        float
            Infectiousness parameter of household

        """
        closure_inf = Parameters.instance().\
            intervention_params['place_closure'][
                'closure_household_infectiousness'] \
            if (hasattr(infector.microcell, 'closure_start_time')) and (
                infector.is_place_closed(
                    Parameters.instance().intervention_params[
                        'place_closure']['closure_place_type'])) and (
                            infector.microcell.closure_start_time <= time
                        ) else 1
        household_infectiousness = PersonalInfection.person_inf(
            infector, time) * closure_inf
        return household_infectiousness

    @staticmethod
    def household_susc(infector, infectee, time: float):
        """Calculate the susceptibility of one person to another in a given
        household. Does not include interventions such as isolation,
        or whether individual is a carehome resident.

        Parameters
        ----------
        infector : Person
            Infector
        infectee : Person
            Infectee
        time : float
            Current simulation time

        Returns
        -------
        float
            Susceptibility parameter of household

        """
        household_susceptibility = PersonalInfection.person_susc(
            infector, infectee, time)
        if (hasattr(infector.microcell, 'distancing_start_time')) and (
                infector.microcell.distancing_start_time is not None) and (
                    infector.microcell.distancing_start_time <= time):
            if infector.distancing_enhanced is True:
                household_susceptibility *= Parameters.instance().\
                    intervention_params['social_distancing'][
                        'distancing_house_enhanced_susc']
            else:
                household_susceptibility *= Parameters.instance().\
                    intervention_params['social_distancing'][
                        'distancing_house_susc']
        return household_susceptibility

    @staticmethod
    def household_foi(infector, infectee, time: float):
        """Calculate the force of infection parameter of a household,
        for a particular infector and infectee.

        Parameters
        ----------
        infector : Person
            Infector
        infectee : Person
            Infectee
        time : float
            Current simulation time

        Returns
        -------
        float
            Force of infection parameter of household

        """
        carehome_scale_inf = 1
        if infector.care_home_resident:
            carehome_scale_inf = Parameters.instance()\
                .carehome_params["carehome_resident_household_scaling"]
        carehome_scale_susc = 1
        if infectee.care_home_resident:
            carehome_scale_susc = Parameters.instance()\
                .carehome_params["carehome_resident_household_scaling"]
        seasonality = 1.0  # Not yet implemented
        isolating = Parameters.instance().\
            intervention_params['case_isolation']['isolation_house'
                                                  '_effectiveness'] \
            if (hasattr(infector, 'isolation_start_time')) and (
                infector.isolation_start_time is not None) and (
                    infector.isolation_start_time <= time) else 1
        quarantine = Parameters.instance().\
            intervention_params['household_quarantine']['quarantine_house'
                                                        '_effectiveness'] \
            if (hasattr(infector, 'quarantine_start_time')) and (
                infector.quarantine_start_time is not None) and (
                    infector.quarantine_start_time <= time) else 1
        infectiousness = (HouseholdInfection.household_inf(infector, time)
                          * seasonality
                          * pyEpiabm.core.Parameters.instance().
                          household_transmission
                          * carehome_scale_inf
                          * isolating * quarantine)
        susceptibility = (HouseholdInfection.household_susc(infector,
                                                            infectee, time)
                          * carehome_scale_susc)
        return (infectiousness * susceptibility)
