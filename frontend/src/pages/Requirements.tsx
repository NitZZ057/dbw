import { useEffect, useState } from "react";

type RequirementCard = {
  title: string;
  endpoint: string;
  sources: string[];
  justification: string;
};

type ApiResponse<T> = {
  data: T;
  sources?: string[];
};

export function Requirements() {
  const [results, setResults] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(true);

  const requirements: RequirementCard[] = [
    {
      title: "Earliest accident year in complete dataset",
      endpoint: "/time/earliest",
      sources: ["Unfallatlas"],
      justification:
        "Uses SQL MIN(year) across all imported accident records.",
    },
    {
      title: "Personal injury accidents in Saxony (2023)",
      endpoint: "/accidents/count?state_ags=14&year=2023",
      sources: ["Unfallatlas"],
      justification:
        "Uses SQL COUNT() filtered by Saxony AGS and year 2023.",
    },
    {
      title: "Earliest year available for North Rhine-Westphalia",
      endpoint: "/time/earliest?state_ags=05",
      sources: ["Unfallatlas"],
      justification:
        "Uses SQL MIN(year) filtered by AGS prefix 05.",
    },
    {
      title: "Earliest year available for Mecklenburg-Western Pomerania",
      endpoint: "/time/earliest?state_ags=13",
      sources: ["Unfallatlas"],
      justification:
        "Uses SQL MIN(year) filtered by AGS prefix 13.",
    },
    {
      title: "Pedestrian accidents in Berlin (2023)",
      endpoint: "/accidents/count?state_ags=11&year=2023&ist_fuss=true",
      sources: ["Unfallatlas"],
      justification:
        "Counts accidents involving pedestrians in Berlin during 2023.",
    },
    {
      title: "District accident rates per 100,000 inhabitants",
      endpoint: "/aggregates/rates?year=2023&level=district&top_n=10",
      sources: ["Unfallatlas", "GENESIS"],
      justification:
        "Combines accident counts and population data to calculate rates.",
    },
    {
      title: "Compare calculated rates with Regionalstatistik",
      endpoint: "/aggregates/rate-comparison",
      sources: ["Unfallatlas", "GENESIS", "Regionalstatistik"],
      justification:
        "Compares calculated accident rates with published Regionalstatistik indicators.",
    },
  ];

  useEffect(() => {
    const load = async () => {
      const entries = await Promise.all(
        requirements.map(async (req) => {
          try {
            const response = await fetch(
              `http://localhost:8000${req.endpoint}`
            );

            const data: ApiResponse<unknown> = await response.json();

            return [req.endpoint, data.data];
          } catch {
            return [req.endpoint, "Error"];
          }
        })
      );

      setResults(Object.fromEntries(entries));
      setLoading(false);
    };

    load();
  }, []);

  return (
    <div>
      <h1>Project Requirements Demonstration</h1>

      <p>
        This page demonstrates all mandatory project questions and
        cross-source aggregations.
      </p>

      {loading && <p>Loading...</p>}

      {requirements.map((req) => (
        <div
          key={req.endpoint}
          style={{
            border: "1px solid #ddd",
            borderRadius: 8,
            padding: 16,
            marginBottom: 16,
          }}
        >
          <h3>{req.title}</h3>

          <p>
            <strong>Endpoint:</strong> {req.endpoint}
          </p>

          <p>
            <strong>Sources:</strong>{" "}
            {req.sources.join(", ")}
          </p>

          <p>
            <strong>Justification:</strong>{" "}
            {req.justification}
          </p>

          <details>
            <summary>Show Result</summary>

            <pre
              style={{
                overflowX: "auto",
                background: "#f5f5f5",
                padding: 12,
              }}
            >
              {JSON.stringify(
                results[req.endpoint],
                null,
                2
              )}
            </pre>
          </details>
        </div>
      ))}
    </div>
  );
}