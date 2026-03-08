/**
 * Parses unstructured API response text into structured defects.
 * Used when the API returns free-form text instead of structured JSON.
 */

export type Defect = {
    id: string;
    severity: "critical" | "major" | "minor";
    description: string;
};

/** Normalize API (high/med/low) or VLM severity string to defect severity. */
export function normalizeSeverityToDefect(s: string | null | undefined): Defect["severity"] {
    if (s === "high" || s === "critical") return "critical";
    if (s === "med" || s === "major") return "major";
    if (s === "low" || s === "minor") return "minor";
    return "major";
}

const METADATA_LABEL_RE =
    /^(object\s+classification|approximate\s+location|location|severity(\s+rating)?|confidence(\s+score)?|recommended\s+action)\s*[:\s]/i;

function isMetadataContent(text: string): boolean {
    const cleaned = text.trim().replace(/^(the|a|an|this)\s+/i, "");
    return METADATA_LABEL_RE.test(cleaned);
}

function cleanDescription(desc: string): string {
    return desc.replace(METADATA_LABEL_RE, "").trim();
}

function isMetadataLine(line: string): boolean {
    // Strip leading bullet chars so both "- Location:" and "• Location:" are caught
    const inner = line.toLowerCase().replace(/^[•\-*\s]+/, "");
    return isMetadataContent(inner);
}

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

        // Skip metadata lines entirely (location, severity, confidence, recommended action, etc.)
        if (defects.length > 0 && isMetadataLine(line)) {
            continue;
        }

        // Extract bullet points as defect descriptions
        const bulletMatch = line.match(/^[\s]*[•\-*]\s*(.+)/);
        if (bulletMatch && currentSeverity) {
            const content = bulletMatch[1].trim();
            if (isMetadataContent(content)) continue;
            const desc = cleanDescription(content);
            if (desc.length > 5) {
                defects.push({
                    id: `DEF-${String(defectIndex + 1).padStart(3, "0")}`,
                    severity: currentSeverity,
                    description: desc,
                });
                defectIndex++;
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
                severity: response.toLowerCase().includes("critical") ? "critical" : "major",
                description: snippet || "Anomaly detected (see full analysis below)",
            });
        }
    }

    return defects;
}
