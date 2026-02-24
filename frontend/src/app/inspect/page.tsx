"use client";

/**
 * Page for creating a new inspection.
 * Upload an image to run FOD (Foreign Object Debris) detection.
 * Styled after AI Anomaly Detection Tool Dashboard.
 */

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Image, FileText, AlertCircle } from "lucide-react";
import { useApp } from "@/app/AppProvider";
import { detectFod } from "@/lib/api";
import { saveInspection } from "@/lib/inspection-store";

export default function InspectPage() {
    const router = useRouter();
    const { currentProject } = useApp();
    const [productPhoto, setProductPhoto] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleProductPhotoUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        setError(null);
        if (file) {
            if (!file.type.startsWith("image/")) {
                setError("Please select an image file (PNG, JPG, etc.)");
                return;
            }
            setPreviewUrl((prev) => {
                if (prev) URL.revokeObjectURL(prev);
                return URL.createObjectURL(file);
            });
            setProductPhoto(file);
        } else {
            setPreviewUrl((prev) => {
                if (prev) URL.revokeObjectURL(prev);
                return null;
            });
            setProductPhoto(null);
        }
        e.target.value = "";
    }, []);

    const handleDrop = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault();
            const file = e.dataTransfer.files?.[0];
            if (file && file.type.startsWith("image/")) {
                setError(null);
                setPreviewUrl((prev) => {
                    if (prev) URL.revokeObjectURL(prev);
                    return URL.createObjectURL(file);
                });
                setProductPhoto(file);
            } else if (file) {
                setError("Please drop an image file (PNG, JPG, etc.)");
            }
        },
        [],
    );

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = "copy";
    }, []);

    const removeProductPhoto = () => {
        setPreviewUrl((prev) => {
            if (prev) URL.revokeObjectURL(prev);
            return null;
        });
        setProductPhoto(null);
        setError(null);
    };

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
        if (!productPhoto) return;
        setIsAnalyzing(true);
        setError(null);
        const imageUrl = previewUrl ?? URL.createObjectURL(productPhoto);
        const basePayload = {
            imageUrl,
            timestamp: new Date().toISOString(),
            projectId: currentProject?.id,
            projectName: currentProject?.name,
        };
        try {
            const result = await detectFod(productPhoto);
            const id = saveInspection({
                ...basePayload,
                response: result.response,
                model: result.model,
                inferenceTimeMs: result.inference_time_ms,
            });
            router.push(`/inspect/result/${id}`);
        } catch {
            // API failed: save mock result and show result page anyway
            const id = saveInspection({
                ...basePayload,
                response: MOCK_RESPONSE,
                model: "mock (offline)",
                inferenceTimeMs: 0,
            });
            router.push(`/inspect/result/${id}`);
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="flex-1 flex flex-col bg-slate-50 dark:bg-zinc-950 transition-colors overflow-hidden">
            <div className="max-w-[700px] w-full mx-auto flex-1 flex flex-col py-6">
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
                    New Inspection
                </h1>
                <p className="text-slate-600 dark:text-zinc-400 mb-6">
                    Upload product photos for analysis against project specifications
                </p>

                {/* Design Specifications Info */}
                {currentProject && currentProject.designSpecs.length > 0 && (
                    <div className="mb-8 bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 rounded-xl p-4">
                        <div className="flex items-start gap-3">
                            <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-1">
                                    Design Specifications
                                </p>
                                <div className="space-y-1">
                                    {currentProject.designSpecs.map((spec, index) => (
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

                {/* Upload Product Photo */}
                <div>
                    <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                        Upload Product Photo
                    </h3>

                    {!productPhoto ? (
                        <div
                            onDrop={handleDrop}
                            onDragOver={handleDragOver}
                            className="border-2 border-dashed border-slate-300 dark:border-zinc-700 rounded-xl p-12 text-center bg-white dark:bg-zinc-900/50 hover:border-blue-400 dark:hover:border-blue-600 transition-colors"
                        >
                            <input
                                type="file"
                                id="product-photo"
                                onChange={handleProductPhotoUpload}
                                accept="image/*"
                                className="hidden"
                            />
                            <label htmlFor="product-photo" className="cursor-pointer block">
                                <Image className="w-12 h-12 text-slate-400 dark:text-zinc-600 mx-auto mb-4" />
                                <p className="text-slate-900 dark:text-white mb-1">
                                    Drop Product Photo here or{" "}
                                    <span className="text-blue-600 dark:text-blue-400 font-medium">
                                        browse
                                    </span>
                                </p>
                                <p className="text-sm text-slate-500 dark:text-zinc-500">
                                    PNG, JPG, JPEG, WebP
                                </p>
                            </label>
                        </div>
                    ) : (
                        <div className="relative group bg-slate-100 dark:bg-zinc-800 rounded-xl overflow-hidden border-2 border-slate-200 dark:border-zinc-700">
                            <img
                                src={previewUrl ?? ""}
                                alt={productPhoto.name}
                                className="w-full h-auto"
                            />
                            <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
                                <label
                                    htmlFor="product-photo"
                                    className="bg-white dark:bg-zinc-900 text-slate-900 dark:text-white px-4 py-2 rounded-lg font-medium cursor-pointer hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors"
                                >
                                    Replace
                                </label>
                                <button
                                    onClick={removeProductPhoto}
                                    disabled={isAnalyzing}
                                    className="bg-red-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-600 transition-colors disabled:opacity-50"
                                >
                                    Remove
                                </button>
                            </div>
                            <input
                                type="file"
                                id="product-photo"
                                onChange={handleProductPhotoUpload}
                                accept="image/*"
                                className="hidden"
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
                    onClick={handleRunInspection}
                    disabled={!productPhoto || isAnalyzing}
                    className={`w-full font-semibold py-4 px-6 rounded-xl transition-all disabled:cursor-not-allowed shadow-sm mt-8 ${
                        productPhoto && !isAnalyzing
                            ? "bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 hover:dark:bg-blue-600 text-white"
                            : "bg-slate-300 dark:bg-zinc-800 text-slate-500 dark:text-zinc-600"
                    }`}
                >
                    {isAnalyzing ? (
                        <span className="flex items-center justify-center gap-3">
                            <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                            Analyzing Product...
                        </span>
                    ) : (
                        "Start Analysis"
                    )}
                </button>

                {!currentProject && (
                    <p className="mt-4 text-sm text-amber-600 dark:text-amber-400">
                        No project selected. Switch project from the header.
                    </p>
                )}
            </div>
        </div>
    );
}
