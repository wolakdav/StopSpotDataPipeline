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
            data (Pandas.DataFrame): The dataset to find duplicates in. This
                    must have a 'service_date' field, otherwise an ValueError
                    is thrown.

        Returns: 
            pandas.DataFrame: The DF with index row_id and field service_date
                    of rows that are duplicates.

        Raises:
            ValueError: When the input pandas.DataFrame lacks a 'service_date' field.
        """

        duplicates = data[data.duplicated(keep=False)]
        try:
            duplicates = duplicates['service_date'].to_frame()
        except KeyError:
            raise ValueError('Duplicate.flag() received a pandas.DataFrame without a "service_date" field.')
        return duplicates

flaggers.append(Duplicate())
