"use client";

/**
 * Page for creating a new inspection.
 * Supports multiple product photos with batch processing and per-image progress.
 * Styled after AI Anomaly Detection Tool Dashboard.
 * Stays on dashboard after analysis (adds to history, no auto-navigation).
 */

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Image, FileText, AlertCircle, X } from "lucide-react";
import { useApp } from "@/app/AppProvider";
import { detectFod } from "@/lib/api";
import { saveInspectionBatch } from "@/lib/inspection-store";
import { parseDefectsFromResponse } from "@/lib/defect-parser";

export default function InspectPage() {
    const router = useRouter();
    const { currentProject } = useApp();

    // Inspect requires a project - redirect to select one if missing
    useEffect(() => {
        if (!currentProject) {
            router.replace("/projects");
        }
    }, [currentProject, router]);
    const [productPhotos, setProductPhotos] = useState<File[]>([]);
    const [previewUrls, setPreviewUrls] = useState<string[]>([]);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisProgress, setAnalysisProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);

    const handleProductPhotoUpload = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            const files = e.target.files;
            setError(null);
            if (files && files.length > 0) {
                const newFiles = Array.from(files).filter((f) =>
                    f.type.startsWith("image/")
                );
                const newUrls = newFiles.map((f) => URL.createObjectURL(f));
                setProductPhotos((prev) => [...prev, ...newFiles]);
                setPreviewUrls((prev) => [...prev, ...newUrls]);
            }
            e.target.value = "";
        },
        []
    );

    const removeProductPhoto = useCallback((index: number) => {
        setProductPhotos((prev) => prev.filter((_, i) => i !== index));
        setPreviewUrls((prev) => {
            const url = prev[index];
            if (url) URL.revokeObjectURL(url);
            return prev.filter((_, i) => i !== index);
        });
        setError(null);
    }, []);

    const clearAllPhotos = useCallback(() => {
        previewUrls.forEach((u) => URL.revokeObjectURL(u));
        setProductPhotos([]);
        setPreviewUrls([]);
        setError(null);
    }, [previewUrls]);

    const MOCK_RESPONSE = `INSPECTION SUMMARY (Mock - API unavailable)

Specification: Design specs
Images Analyzed: 1
Defects Detected: 2 anomalies found
Status: FAIL - Defects present

CRITICAL FAILURES:
• Surface Integrity: Foreign object detected
  - Location: Upper-left quadrant
  - Recommended Action: Reject and rework

MAJOR ISSUES:
• Debris detected at center region
  - Recommended Action: Quality review required

RECOMMENDATION: Product does not meet manufacturing specifications. Immediate rework required.`;

    const handleRunInspection = async () => {
        if (productPhotos.length === 0) return;
        setIsAnalyzing(true);
        setError(null);
        setAnalysisProgress(0);

        const designSpecs = currentProject?.designSpecs ?? [];
        const submissions: Array<{
            timestamp: string;
            productPhoto: string;
            photoName: string;
            designSpec: string[];
            status: "pass" | "fail";
            defects: ReturnType<typeof parseDefectsFromResponse>;
            analysis: string;
            model?: string;
            inferenceTimeMs?: number;
        }> = [];

        const total = productPhotos.length;
        let processed = 0;

        for (let i = 0; i < productPhotos.length; i++) {
            const file = productPhotos[i];
            const imageUrl = previewUrls[i] ?? URL.createObjectURL(file);

            try {
                const result = await detectFod(file);
                const defects = parseDefectsFromResponse(result.response);
                const status =
                    defects.some((d) => d.severity === "critical") ||
                    result.response.toLowerCase().includes("fail")
                        ? "fail"
                        : "pass";

                submissions.push({
                    timestamp: new Date().toISOString(),
                    productPhoto: imageUrl,
                    photoName: file.name,
                    designSpec: designSpecs,
                    status,
                    defects,
                    analysis: result.response,
                    model: result.model,
                    inferenceTimeMs: result.inference_time_ms,
                });
            } catch {
                const defects = parseDefectsFromResponse(MOCK_RESPONSE);
                submissions.push({
                    timestamp: new Date().toISOString(),
                    productPhoto: imageUrl,
                    photoName: file.name,
                    designSpec: designSpecs,
                    status: "fail",
                    defects,
                    analysis: MOCK_RESPONSE,
                    model: "mock (offline)",
                    inferenceTimeMs: 0,
                });
            }

            processed++;
            setAnalysisProgress(Math.round((processed / total) * 100));
        }

        saveInspectionBatch({
            submissions,
            projectId: currentProject?.id,
            projectName: currentProject?.name,
            designSpecs,
        });

        setIsAnalyzing(false);
        setProductPhotos([]);
        // Do NOT revoke blob URLs - they're stored in the batch and needed for display
        setPreviewUrls([]);

        // Stay on dashboard - do NOT navigate. History sidebar will update.
    };

    const designSpecs = currentProject?.designSpecs ?? [];

    return (
        <div className="flex-1 flex flex-col bg-slate-50 dark:bg-zinc-950 transition-colors overflow-hidden">
                <div className="max-w-[700px] w-full mx-auto flex-1 flex flex-col py-6">
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
                        New Inspection
                    </h1>
                    <p className="text-slate-600 dark:text-zinc-400 mb-6">
                        Upload product photos for analysis against project
                        specifications
                    </p>

                    {/* Design Specifications Info */}
                    {currentProject && designSpecs.length > 0 && (
                        <div className="mb-8 bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 rounded-xl p-4">
                            <div className="flex items-start gap-3">
                                <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-1">
                                        Design Specifications
                                    </p>
                                    <div className="space-y-1">
                                        {designSpecs.map((spec, index) => (
                                            <p
                                                key={index}
                                                className="text-sm text-blue-700 dark:text-blue-300 truncate"
                                            >
                                                • {spec}
                                            </p>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Upload Product Photos */}
                    <div>
                        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                            Upload Product Photos
                        </h3>

                        {productPhotos.length === 0 ? (
                            <div
                                onDrop={(e) => {
                                    e.preventDefault();
                                    const files = Array.from(
                                        e.dataTransfer.files
                                    ).filter((f) => f.type.startsWith("image/"));
                                    if (files.length > 0) {
                                        setError(null);
                                        setProductPhotos((p) => [...p, ...files]);
                                        setPreviewUrls((p) => [
                                            ...p,
                                            ...files.map((f) =>
                                                URL.createObjectURL(f)
                                            ),
                                        ]);
                                    }
                                }}
                                onDragOver={(e) => {
                                    e.preventDefault();
                                    e.dataTransfer.dropEffect = "copy";
                                }}
                                className="border-2 border-dashed border-slate-300 dark:border-zinc-700 rounded-xl p-12 text-center bg-white dark:bg-zinc-900/50 hover:border-blue-400 dark:hover:border-blue-600 transition-colors"
                            >
                                <input
                                    type="file"
                                    id="product-photo"
                                    onChange={handleProductPhotoUpload}
                                    accept="image/*"
                                    className="hidden"
                                    multiple
                                />
                                <label
                                    htmlFor="product-photo"
                                    className="cursor-pointer block"
                                >
                                    <Image className="w-12 h-12 text-slate-400 dark:text-zinc-600 mx-auto mb-4" />
                                    <p className="text-slate-900 dark:text-white mb-1">
                                        Drop Product Photos here or{" "}
                                        <span className="text-blue-600 dark:text-blue-400 font-medium">
                                            browse
                                        </span>
                                    </p>
                                    <p className="text-sm text-slate-500 dark:text-zinc-500">
                                        PNG, JPG, JPEG, WebP • Multiple images
                                        supported
                                    </p>
                                </label>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                <div className="grid grid-cols-3 gap-3 p-3 bg-slate-100 dark:bg-zinc-800 rounded-xl border-2 border-slate-200 dark:border-zinc-700">
                                    {productPhotos.map((photo, index) => (
                                        <div
                                            key={index}
                                            className="relative group/photo"
                                        >
                                            <img
                                                src={previewUrls[index] ?? ""}
                                                alt={photo.name}
                                                className="w-full h-auto rounded-lg object-cover aspect-square"
                                            />
                                            <button
                                                type="button"
                                                onClick={() =>
                                                    removeProductPhoto(index)
                                                }
                                                disabled={isAnalyzing}
                                                className="absolute top-1 right-1 bg-red-500 text-white p-1.5 rounded-lg opacity-0 group-hover/photo:opacity-100 transition-opacity hover:bg-red-600 disabled:opacity-50"
                                                title="Remove"
                                            >
                                                <X className="w-4 h-4" />
                                            </button>
                                            <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-xs p-1 rounded-b-lg truncate">
                                                {photo.name}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                <div className="flex gap-2">
                                    <label
                                        htmlFor="product-photo-add"
                                        className="flex-1 bg-slate-200 dark:bg-zinc-700 hover:bg-slate-300 dark:hover:bg-zinc-600 text-slate-900 dark:text-white px-4 py-2 rounded-lg font-medium cursor-pointer transition-colors text-center disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        Add More Photos
                                    </label>
                                    <button
                                        type="button"
                                        onClick={clearAllPhotos}
                                        disabled={isAnalyzing}
                                        className="bg-red-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-600 transition-colors disabled:opacity-50"
                                    >
                                        Clear All
                                    </button>
                                </div>
                                <input
                                    type="file"
                                    id="product-photo-add"
                                    onChange={handleProductPhotoUpload}
                                    accept="image/*"
                                    className="hidden"
                                    multiple
                                />
                            </div>
                        )}
                    </div>

                    {error && (
                        <div className="mt-4 flex items-center gap-2 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300">
                            <AlertCircle className="w-5 h-5 flex-shrink-0" />
                            <p className="text-sm">{error}</p>
                        </div>
                    )}

                    {/* Start Analysis Button */}
                    <button
                        type="button"
                        onClick={handleRunInspection}
                        disabled={
                            productPhotos.length === 0 || isAnalyzing
                        }
                        className={`w-full font-semibold py-4 px-6 rounded-xl transition-all disabled:cursor-not-allowed shadow-sm mt-8 ${
                            productPhotos.length && !isAnalyzing
                                ? "bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 hover:dark:bg-blue-600 text-white"
                                : "bg-slate-300 dark:bg-zinc-800 text-slate-500 dark:text-zinc-600"
                        }`}
                    >
                        {isAnalyzing ? (
                            <span className="flex flex-col items-center gap-2">
                                <span className="flex items-center gap-3">
                                    <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                                    Analyzing {productPhotos.length} Product
                                    {productPhotos.length > 1 ? "s" : ""}...
                                </span>
                                <div className="w-full bg-slate-400 dark:bg-zinc-700 rounded-full h-2 overflow-hidden">
                                    <div
                                        className="bg-white h-full transition-all duration-300"
                                        style={{
                                            width: `${analysisProgress}%`,
                                        }}
                                    />
                                </div>
                                <span className="text-sm">
                                    {analysisProgress}%
                                </span>
                            </span>
                        ) : (
                            "Start Analysis"
                        )}
                    </button>

                </div>
        </div>
    );
}
