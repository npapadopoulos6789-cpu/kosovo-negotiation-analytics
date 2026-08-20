// Hook που φέρνει όλες τις χώρες μία φορά και τις εκθέτει σαν Map<id, Country>
// για O(1) lookup -- χρήσιμο παντού όπου έχουμε μόνο country_id (events,
// indicators, participants) και θέλουμε να δείξουμε όνομα/geopolitical_bloc
// χωρίς extra fetch ανά εγγραφή. react-query κάνει cache το αποτέλεσμα, άρα
// πολλαπλά components που καλούν το hook ταυτόχρονα μοιράζονται ένα request.

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { listCountries } from "../api/countries";
import type { Country } from "../api/types";

export function useCountryLookup() {
  const query = useQuery({
    queryKey: ["countries"],
    queryFn: listCountries,
  });

  // useMemo -- χωρίς αυτό θα φτιαχνόταν καινούριο Map σε κάθε render, άρα
  // νέα referential identity, άρα οποιοδήποτε useEffect/useMemo consumer με
  // countryMap σε dependency array θα έτρεχε ξανά χωρίς λόγο.
  const countryMap = useMemo(
    () => new Map<number, Country>((query.data ?? []).map((country) => [country.id, country])),
    [query.data],
  );

  return {
    ...query,
    countryMap,
  };
}
