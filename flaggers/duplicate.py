from .flagger import Flagger, Flags, flaggers

# Class implements duplicate check
class Duplicate(Flagger):
    name = 'Duplicate'

    def flag(self, data):
        """
        Due to this flag being an oddity, this method will return a DataFrame
        of service_dates that are duplicates. It is the responsibility of the
        caller to process these into whatever form they desire.

        Args:
            data (Pandas.DataFrame): The dataset to find duplicates in.

        Returns: 
            pandas.DataFrame: The DF with index row_id and field service_date
                                of rows that are duplicates.
        """

        duplicates = data[data.duplicated(keep=False)]
        duplicates = duplicates["service_date"].to_frame()
        return duplicates

flaggers.append(Duplicate())
