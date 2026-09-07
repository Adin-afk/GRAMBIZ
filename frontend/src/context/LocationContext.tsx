import { createContext, useContext, useState, type ReactNode } from "react";
import type { Taluka, Village } from "../types/api";

interface LocationContextValue {
  taluka: Taluka | null;
  village: Village | null;
  availableCapital: number | null;
  setTaluka: (t: Taluka | null) => void;
  setVillage: (v: Village | null) => void;
  setAvailableCapital: (c: number | null) => void;
}

const LocationContext = createContext<LocationContextValue | undefined>(undefined);

export function LocationProvider({ children }: { children: ReactNode }) {
  const [taluka, setTaluka] = useState<Taluka | null>(null);
  const [village, setVillage] = useState<Village | null>(null);
  const [availableCapital, setAvailableCapital] = useState<number | null>(null);

  return (
    <LocationContext.Provider
      value={{ taluka, village, availableCapital, setTaluka, setVillage, setAvailableCapital }}
    >
      {children}
    </LocationContext.Provider>
  );
}

export function useLocationContext() {
  const ctx = useContext(LocationContext);
  if (!ctx) throw new Error("useLocationContext must be used within LocationProvider");
  return ctx;
}
