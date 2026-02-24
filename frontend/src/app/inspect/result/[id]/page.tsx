"use client";

/**
 * Page for viewing the result of an inspection.
 * PDF-style report layout based on AI Anomaly Detection Tool ResultsView.
 */

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
    ChevronLeft,
    Download,
    Calendar,
    FileCheck,
    AlertCircle,
} from "lucide-react";
import { useApp } from "@/app/AppProvider";
import {
    getInspection,
    deriveStatus,
    type InspectionResult,
} from "@/lib/inspection-store";

export default function InspectResultPage() {
    const params = useParams();
    const router = useRouter();
    const { currentProject } = useApp();
    const id = typeof params.id === "string" ? params.id : "";
    const [result, setResult] = useState<InspectionResult | null>(null);
    const [notFound, setNotFound] = useState(false);

    useEffect(() => {
        if (!id) {
            setNotFound(true);
            return;
        }
        const data = getInspection(id);
        if (data) {
            setResult(data);
        } else {
            setNotFound(true);
        }
    }, [id]);

    const handleDownloadPDF = () => {
        alert(
            "PDF Report would be downloaded here. In production, this would generate and download a PDF file with the inspection results.",
        );
    };

    if (notFound) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center bg-slate-50 dark:bg-zinc-950 py-12 px-6">
                <div className="max-w-md text-center">
                    <AlertCircle className="w-16 h-16 text-amber-500 mx-auto mb-4" />
                    <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                        Inspection Not Found
                    </h2>
                    <p className="text-slate-600 dark:text-zinc-400 mb-6">
                        This inspection may have expired or the link is invalid.
                        Results are stored in your session and are cleared when you
                        close the browser.
                    </p>
                    <button
                        onClick={() => router.push("/inspect")}
                        className="flex items-center gap-2 text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white transition-colors font-medium"
                    >
                        <ChevronLeft className="w-5 h-5" />
                        Back to New Inspection
                    </button>
                </div>
            </div>
        );
    }

    if (!result) {
        return (
            <div className="flex-1 flex items-center justify-center bg-slate-50 dark:bg-zinc-950">
                <div className="animate-pulse text-muted-foreground">Loading...</div>
            </div>
        );
    }

    const status = deriveStatus(result.response);
    const today = new Date(result.timestamp).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
    });
    const overallStatus = status === "pass" ? "PASS" : "FAIL";
    const designSpecs = currentProject?.designSpecs ?? [];

    return (
        <div className="flex-1 flex flex-col bg-slate-50 dark:bg-zinc-950 transition-colors overflow-hidden">
            <div className="max-w-[1200px] w-full mx-auto flex-1 flex flex-col py-6">
                {/* Back Button */}
                <button
                    onClick={() => router.push("/inspect")}
                    className="flex items-center gap-2 text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white mb-6 transition-colors font-medium"
                >
                    <ChevronLeft className="w-5 h-5" />
                    <span>Back to New Inspection</span>
                </button>

                {/* Action Buttons */}
                <div className="flex gap-4 mb-6">
                    <button
                        onClick={handleDownloadPDF}
                        className="flex-1 bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600 text-white font-semibold py-4 px-6 rounded-xl transition-all shadow-sm flex items-center justify-center gap-2"
                    >
                        <Download className="w-5 h-5" />
                        Download PDF Report
                    </button>
                    <button
                        onClick={() => router.push("/inspect")}
                        className="flex-1 bg-slate-200 dark:bg-zinc-800 hover:bg-slate-300 dark:hover:bg-zinc-700 text-slate-900 dark:text-white font-semibold py-4 px-6 rounded-xl transition-all"
                    >
                        New Inspection
                    </button>
                </div>

                {/* PDF-Style Report Preview */}
                <div className="bg-white dark:bg-zinc-900 rounded-lg shadow-lg border border-slate-200 dark:border-zinc-800 overflow-hidden">
                    {/* Report Header */}
                    <div className="bg-slate-100 dark:bg-zinc-800 px-8 py-6 border-b border-slate-200 dark:border-zinc-700">
                        <div className="flex items-start justify-between mb-4">
                            <div>
                                <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-1">
                                    Quality Inspection Report
                                </h1>
                                <p className="text-slate-600 dark:text-zinc-400">
                                    AI-Powered Anomaly Detection Analysis
                                </p>
                            </div>
                            <div className="text-right">
                                <div className="flex items-center gap-2 text-slate-600 dark:text-zinc-400 text-sm mb-1">
                                    <Calendar className="w-4 h-4" />
                                    <span>{today}</span>
                                </div>
                                <div
                                    className={`inline-block px-3 py-1 rounded-full font-bold text-sm ${
                                        overallStatus === "FAIL"
                                            ? "bg-red-100 dark:bg-red-500/10 text-red-700 dark:text-red-400"
                                            : "bg-green-100 dark:bg-green-500/10 text-green-700 dark:text-green-400"
                                    }`}
                                >
                                    {overallStatus}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Report Content */}
                    <div className="p-8">
                        {/* Inspection Summary */}
                        <section className="mb-8">
                            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                                <FileCheck className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                                Inspection Summary
                            </h2>

                            {/* Design Specifications */}
                            {designSpecs.length > 0 && (
                                <div className="bg-slate-50 dark:bg-zinc-800 rounded-lg p-4 border border-slate-200 dark:border-zinc-700 mb-4">
                                    <p className="text-sm text-slate-600 dark:text-zinc-400 mb-3 font-semibold">
                                        Design Specifications ({designSpecs.length})
                                    </p>
                                    <div className="max-h-40 overflow-y-auto pr-2">
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                                            {designSpecs.map((spec, index) => (
                                                <div
                                                    key={index}
                                                    className="flex items-start gap-2"
                                                >
                                                    <span className="text-slate-400 dark:text-zinc-600 text-sm mt-0.5">
                                                        •
                                                    </span>
                                                    <p className="text-sm text-slate-900 dark:text-white flex-1 break-words">
                                                        {spec}
                                                    </p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Stats / Metadata */}
                            <div className="grid grid-cols-2 gap-4">
                                {result.projectName && (
                                    <div className="bg-slate-50 dark:bg-zinc-800 rounded-lg p-4 border border-slate-200 dark:border-zinc-700">
                                        <p className="text-sm text-slate-600 dark:text-zinc-400 mb-1">
                                            Project
                                        </p>
                                        <p className="text-lg font-bold text-slate-900 dark:text-white">
                                            {result.projectName}
                                        </p>
                                    </div>
                                )}
                                {(result.model || result.inferenceTimeMs != null) && (
                                    <div className="bg-slate-50 dark:bg-zinc-800 rounded-lg p-4 border border-slate-200 dark:border-zinc-700">
                                        <p className="text-sm text-slate-600 dark:text-zinc-400 mb-1">
                                            Model / Inference
                                        </p>
                                        <p className="text-sm font-medium text-slate-900 dark:text-white">
                                            {result.model && <span>{result.model}</span>}
                                            {result.model &&
                                                result.inferenceTimeMs != null &&
                                                " · "}
                                            {result.inferenceTimeMs != null && (
                                                <span>
                                                    {result.inferenceTimeMs.toFixed(0)}ms
                                                </span>
                                            )}
                                        </p>
                                    </div>
                                )}
                            </div>
                        </section>

                        {/* Product Image */}
                        <section className="mb-8">
                            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4">
                                Product Image
                            </h2>
                            <div className="relative bg-slate-100 dark:bg-zinc-800 rounded-lg overflow-hidden border border-slate-200 dark:border-zinc-700">
                                <img
                                    src={result.imageUrl}
                                    alt="Product"
                                    className="w-full h-auto"
                                />
                            </div>
                        </section>

                        {/* Detailed Analysis */}
                        <section>
                            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4">
                                Detailed Analysis
                            </h2>
                            <div className="bg-slate-50 dark:bg-zinc-800 rounded-lg p-6 border border-slate-200 dark:border-zinc-700">
                                <pre className="whitespace-pre-wrap font-mono text-sm text-slate-700 dark:text-zinc-300 leading-relaxed">
                                    {result.response}
                                </pre>
                            </div>
                        </section>
                    </div>

                    {/* Report Footer */}
                    <div className="bg-slate-100 dark:bg-zinc-800 px-8 py-4 border-t border-slate-200 dark:border-zinc-700">
                        <p className="text-sm text-slate-600 dark:text-zinc-400 text-center">
                            Generated by GLaDOS AI Anomaly Detection System • {today}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
