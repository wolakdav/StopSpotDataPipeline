from .flagger import Flagger, Flags, flaggers
import numpy as np
import pandas as pd

#Class implements duplicate check
class Duplicate(Flagger):
    name = 'Duplicate'

    def flag(self, row, data):
        """
        Checks passed row/dict/object and passed full dataset, to see if there are duplicates.
        This is a special flagger that requires a special call.

        Args:
            row (Object): data row from full dataset fetched from the db
            data (Matrix/List of Objects): full dataset fetched from db

        Returns: 
            list: either empty or containing DUPLICATE Flag
        """

        flag = []

        # Using pandas's duplicated method to get all duplicated rows and then
        # check if this row is in it.
        # Kinda weird but this is the only solution that succinctly solves a few 
        # problems: numpy == doesn't work well with NaN and None values, both
        # of which are present within the Portal's database.
        # TODO: This is a really slow way of flagging duplicates, we definitely
        # should come up with a different way.
        #if row_id in list(np.where(data.duplicated(keep=False))[0]):
        #if row_id in duplicate_list:
            #flag.append(Flags.DUPLICATE)

        #Above check doesn't work because data contains no row_id, and matches happen on any other values which match passed in int (row_id)
        #Note, this still doesn't work with None and NaN, since NaN != NaN, thus no matches
        duplicates = data[data.duplicated(keep=False)]
        matches = duplicates[(duplicates==row.values).all(axis=1)]  #Returns number of matched rows
        match_exists = (duplicates==row.values).all().all()  #Returns whether match exists
        
        #Because of None and NaN need to do this weird double/triple check
        if ((len(matches) >= 1) and (duplicates==row.values).any().any()) or (duplicates==row.values).any().any() : flag.append(Flags.DUPLICATE)

        return flag

flaggers.append(Duplicate())
