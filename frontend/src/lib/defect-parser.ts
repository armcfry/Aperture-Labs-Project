/**
 * Parses unstructured API response text into structured defects.
 * Used when the API returns free-form text instead of structured JSON.
 */

export type Defect = {
    id: string;
    location: { x: number; y: number };
    severity: "critical" | "major" | "minor";
    description: string;
};

// Approximate positions for parsed defects (spread across image when no coords given)
const DEFAULT_POSITIONS: Array<{ x: number; y: number }> = [
    { x: 25, y: 30 },
    { x: 50, y: 50 },
    { x: 75, y: 35 },
    { x: 35, y: 70 },
    { x: 65, y: 65 },
];

export function parseDefectsFromResponse(response: string): Defect[] {
    const defects: Defect[] = [];
    const lines = response.split(/\r?\n/);
    let currentSeverity: Defect["severity"] | null = null;
    let defectIndex = 0;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const lower = line.toLowerCase();

        // Detect severity sections
        if (lower.includes("critical") && (lower.includes("failure") || lower.includes(":"))) {
            currentSeverity = "critical";
        } else if (lower.includes("major") && (lower.includes("issue") || lower.includes(":"))) {
            currentSeverity = "major";
        } else if (lower.includes("minor") && (lower.includes("issue") || lower.includes(":"))) {
            currentSeverity = "minor";
        }

        // Extract bullet points as defect descriptions
        const bulletMatch = line.match(/^[\s]*[•\-*]\s*(.+)/);
        if (bulletMatch && currentSeverity) {
            const desc = bulletMatch[1].trim();
            if (desc.length > 5) {
                const pos = DEFAULT_POSITIONS[defectIndex % DEFAULT_POSITIONS.length];
                defects.push({
                    id: `DEF-${String(defectIndex + 1).padStart(3, "0")}`,
                    location: pos,
                    severity: currentSeverity,
                    description: desc,
                });
                defectIndex++;
            }
        }

        // Also catch "Location:" or "Recommended Action:" continuation lines
        if (defects.length > 0 && (lower.includes("location:") || lower.includes("recommended action:"))) {
            const extra = line.replace(/^[\s\S]*?:\s*/i, "").trim();
            if (extra && defects[defects.length - 1]) {
                defects[defects.length - 1].description += ` (${extra})`;
            }
        }
    }

    // Fallback: if we found nothing structured, create one defect from key phrases
    if (defects.length === 0) {
        const hasFod = /\b(fod|foreign object|debris|defect|anomal)\b/i.test(response);
        if (hasFod) {
            const snippet = response.slice(0, 200).replace(/\s+/g, " ").trim();
            defects.push({
                id: "DEF-001",
                location: { x: 50, y: 50 },
                severity: response.toLowerCase().includes("critical") ? "critical" : "major",
                description: snippet || "Anomaly detected (see full analysis below)",
            });
        }
    }

    return defects;
}
