// Automated αντίστοιχο του χειροκίνητου οπτικού ελέγχου (App.tsx smoke test).
// Mockάρουμε το global fetch -- η ίδια αλυσίδα client.ts -> countries.ts ->
// useCountryLookup τρέχει κανονικά, μόνο το network call είναι ψεύτικο.

import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { useCountryLookup } from "./useCountryLookup";
import type { Country } from "../api/types";

const mockCountries: Country[] = [
  {
    id: 1,
    name: "Serbia",
    actor_type: "STATE",
    geopolitical_bloc: "EAST",
    recognized_kosovo: false,
    country_code: "SRB",
    role_description: null,
  },
  {
    id: 2,
    name: "Kosovo",
    actor_type: "STATE",
    geopolitical_bloc: "WEST",
    recognized_kosovo: null,
    country_code: "XKX",
    role_description: null,
  },
];

function createWrapper() {
  // retry: false -- αλλιώς ένα failed-fetch test θα ξαναδοκίμαζε στο
  // background και θα έκανε το test αργό/flaky
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

describe("useCountryLookup", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("builds a Map keyed by country id with matching values", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => mockCountries,
      }),
    );

    const { result } = renderHook(() => useCountryLookup(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.countryMap.size).toBe(2);
    expect([...result.current.countryMap.keys()]).toEqual([1, 2]);
    expect(result.current.countryMap.get(1)).toEqual(mockCountries[0]);
    expect(result.current.countryMap.get(2)).toEqual(mockCountries[1]);
  });

  it("returns an empty Map while loading, before data arrives", () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => new Promise(() => {})), // ποτέ δεν resolves μέσα στο test
    );

    const { result } = renderHook(() => useCountryLookup(), { wrapper: createWrapper() });

    expect(result.current.isLoading).toBe(true);
    expect(result.current.countryMap.size).toBe(0);
  });

  it("calls the exact /countries path (no trailing slash -- βλ. client.ts)", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [],
    });
    vi.stubGlobal("fetch", fetchMock);

    renderHook(() => useCountryLookup(), { wrapper: createWrapper() });

    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/countries",
      expect.any(Object),
    );
  });
});
