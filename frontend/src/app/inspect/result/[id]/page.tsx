"use client";

/**
 * Page for viewing the result of an inspection.
 * Supports multiple submissions, defect markers on image, severity badges, and stats grid.
 * Based on AI Anomaly Detection Tool ResultsView.
 */

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState, useMemo } from "react";
import {
    ChevronLeft,
    Download,
    Calendar,
    FileCheck,
    FileText,
    AlertCircle,
    AlertTriangle,
    Info,
} from "lucide-react";
import { useApp } from "@/app/AppProvider";
import {
    getInspection,
    toSubmissions,
    deriveStatus,
    type InspectionResult,
    type InspectionSubmission,
    type Defect,
} from "@/lib/inspection-store";

function getSeverityColor(severity: string) {
    switch (severity) {
        case "critical":
            return "text-red-600 dark:text-red-400";
        case "major":
            return "text-orange-600 dark:text-orange-400";
        case "minor":
            return "text-yellow-600 dark:text-yellow-400";
        default:
            return "text-zinc-500 dark:text-zinc-400";
    }
}

function getSeverityBadgeColor(severity: string) {
    switch (severity) {
        case "critical":
            return "bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20";
        case "major":
            return "bg-orange-500/10 text-orange-700 dark:text-orange-400 border-orange-500/20";
        case "minor":
            return "bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-yellow-500/20";
        default:
            return "bg-zinc-500/10 text-zinc-700 dark:text-zinc-400 border-zinc-500/20";
    }
}

function getSeverityIcon(severity: string) {
    switch (severity) {
        case "critical":
            return <AlertCircle className="w-4 h-4" />;
        case "major":
            return <AlertTriangle className="w-4 h-4" />;
        case "minor":
            return <Info className="w-4 h-4" />;
        default:
            return null;
    }
}

export default function InspectResultPage() {
    const params = useParams();
    const router = useRouter();
    const searchParams = useSearchParams();
    const { currentProject } = useApp();
    const id = typeof params.id === "string" ? params.id : "";
    const [result, setResult] = useState<InspectionResult | null>(null);
    const [notFound, setNotFound] = useState(false);

    const selectedSubIds = useMemo(() => {
        const q = searchParams.get("submissions");
        if (!q) return null;
        return new Set(q.split(",").filter(Boolean));
    }, [searchParams]);

    const submissions = useMemo((): InspectionSubmission[] => {
        if (!result) return [];
        const all = toSubmissions(result);
        if (!selectedSubIds || selectedSubIds.size === 0) return all;
        return all.filter((s) => selectedSubIds.has(s.id));
    }, [result, selectedSubIds]);

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
            "PDF Report would be downloaded here. In production, this would generate and download a PDF file with the inspection results."
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
                        Results are stored in your session and are cleared when
                        you close the browser.
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

    if (!result || submissions.length === 0) {
        return (
            <div className="flex-1 flex items-center justify-center bg-slate-50 dark:bg-zinc-950">
                <div className="animate-pulse text-muted-foreground">
                    Loading...
                </div>
            </div>
        );
    }

    const designSpecs =
        (submissions[0]?.designSpec?.length ?? 0) > 0
            ? submissions[0].designSpec
            : currentProject?.designSpecs ?? [];
    const today = new Date(result.timestamp).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
    });
    const hasCritical = submissions.some((s) =>
        s.defects.some((d) => d.severity === "critical")
    );
    const overallStatus = hasCritical ? "FAIL" : "PASS";
    const totalDefects = submissions.reduce(
        (sum, s) => sum + s.defects.length,
        0
    );
    const criticalCount = submissions.reduce(
        (sum, s) =>
            sum + s.defects.filter((d) => d.severity === "critical").length,
        0
    );

    return (
        <div className="flex-1 flex flex-col bg-slate-50 dark:bg-zinc-950 transition-colors overflow-hidden">
            <div className="max-w-[1200px] w-full mx-auto flex-1 flex flex-col py-6">
                {/* Back Button */}
                <button
                    onClick={() => router.push("/inspect")}
                    className="flex items-center gap-2 text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white mb-6 transition-colors font-medium"
                >
                    <ChevronLeft className="w-5 h-5" />
                    <span>Back to Dashboard</span>
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

                {/* Submission Counter */}
                {submissions.length > 1 && (
                    <div className="bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 rounded-xl p-4 mb-6">
                        <div className="flex items-center gap-2">
                            <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                            <span className="text-sm font-semibold text-blue-900 dark:text-blue-100">
                                Viewing {submissions.length} submission
                                {submissions.length > 1 ? "s" : ""} in this
                                report
                            </span>
                        </div>
                    </div>
                )}

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
                                        Design Specifications (
                                        {designSpecs.length})
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

                            {/* Stats Grid */}
                            <div className="grid grid-cols-3 gap-4">
                                <div className="bg-slate-50 dark:bg-zinc-800 rounded-lg p-4 border border-slate-200 dark:border-zinc-700">
                                    <p className="text-sm text-slate-600 dark:text-zinc-400 mb-1">
                                        Total Submissions
                                    </p>
                                    <p className="text-2xl font-bold text-slate-900 dark:text-white">
                                        {submissions.length}
                                    </p>
                                </div>
                                <div className="bg-slate-50 dark:bg-zinc-800 rounded-lg p-4 border border-slate-200 dark:border-zinc-700">
                                    <p className="text-sm text-slate-600 dark:text-zinc-400 mb-1">
                                        Total Defects
                                    </p>
                                    <p className="text-2xl font-bold text-slate-900 dark:text-white">
                                        {totalDefects}
                                    </p>
                                </div>
                                <div className="bg-slate-50 dark:bg-zinc-800 rounded-lg p-4 border border-slate-200 dark:border-zinc-700">
                                    <p className="text-sm text-slate-600 dark:text-zinc-400 mb-1">
                                        Critical Issues
                                    </p>
                                    <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                                        {criticalCount}
                                    </p>
                                </div>
                            </div>

                            {/* Project / Model metadata */}
                            {(result.projectName ||
                                result.model ||
                                result.inferenceTimeMs != null) && (
                                <div className="grid grid-cols-2 gap-4 mt-4">
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
                                    {(result.model ||
                                        result.inferenceTimeMs != null) && (
                                        <div className="bg-slate-50 dark:bg-zinc-800 rounded-lg p-4 border border-slate-200 dark:border-zinc-700">
                                            <p className="text-sm text-slate-600 dark:text-zinc-400 mb-1">
                                                Model / Inference
                                            </p>
                                            <p className="text-sm font-medium text-slate-900 dark:text-white">
                                                {result.model && (
                                                    <span>{result.model}</span>
                                                )}
                                                {result.model &&
                                                    result.inferenceTimeMs !=
                                                        null &&
                                                    " · "}
                                                {result.inferenceTimeMs !=
                                                    null && (
                                                    <span>
                                                        {result.inferenceTimeMs.toFixed(
                                                            0
                                                        )}
                                                        ms
                                                    </span>
                                                )}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </section>

                        {/* All Submissions */}
                        {submissions.map((submission, submissionIndex) => (
                            <div
                                key={submission.id}
                                className={
                                    submissionIndex > 0 ? "mt-12" : ""
                                }
                            >
                                {/* Submission Header */}
                                {submissions.length > 1 && (
                                    <div className="mb-6 pb-4 border-b border-slate-200 dark:border-zinc-700">
                                        <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2 flex-wrap">
                                            <span className="text-blue-600 dark:text-blue-400">
                                                Submission{" "}
                                                {submissionIndex + 1}
                                            </span>
                                            <span className="text-slate-400 dark:text-zinc-600">
                                                /
                                            </span>
                                            <span className="text-sm font-normal text-slate-600 dark:text-zinc-400">
                                                {submission.photoName}
                                            </span>
                                            <span
                                                className={`ml-auto text-sm font-medium px-2.5 py-1 rounded-full ${
                                                    submission.status === "pass"
                                                        ? "bg-green-100 dark:bg-green-500/10 text-green-700 dark:text-green-400"
                                                        : "bg-red-100 dark:bg-red-500/10 text-red-700 dark:text-red-400"
                                                }`}
                                            >
                                                {submission.status.toUpperCase()}
                                            </span>
                                        </h2>
                                    </div>
                                )}

                                {/* Product Image with Defect Markers */}
                                <section className="mb-8">
                                    <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                                        Product Image
                                    </h3>
                                    <div className="relative bg-slate-100 dark:bg-zinc-800 rounded-lg overflow-hidden border border-slate-200 dark:border-zinc-700">
                                        <img
                                            src={submission.productPhoto}
                                            alt={`Product ${submissionIndex + 1}`}
                                            className="w-full h-auto"
                                        />
                                        {submission.defects.map(
                                            (defect: Defect) => (
                                                <div
                                                    key={defect.id}
                                                    className="absolute w-6 h-6 -translate-x-1/2 -translate-y-1/2 cursor-pointer group"
                                                    style={{
                                                        left: `${defect.location.x}%`,
                                                        top: `${defect.location.y}%`,
                                                    }}
                                                >
                                                    <div
                                                        className={`w-6 h-6 rounded-full border-2 flex items-center justify-center animate-pulse ${
                                                            defect.severity ===
                                                            "critical"
                                                                ? "bg-red-500 border-red-300"
                                                                : defect.severity ===
                                                                  "major"
                                                                ? "bg-orange-500 border-orange-300"
                                                                : "bg-yellow-500 border-yellow-300"
                                                        }`}
                                                    >
                                                        <div className="w-2 h-2 bg-white rounded-full" />
                                                    </div>
                                                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-10">
                                                        <div className="bg-slate-900 dark:bg-zinc-800 text-white text-xs rounded-lg py-2 px-3 whitespace-nowrap shadow-lg border border-slate-700 dark:border-zinc-700">
                                                            <p className="font-semibold mb-1">
                                                                {defect.id}
                                                            </p>
                                                            <p
                                                                className={getSeverityColor(
                                                                    defect.severity
                                                                )}
                                                            >
                                                                {defect.severity.toUpperCase()}
                                                            </p>
                                                        </div>
                                                    </div>
                                                </div>
                                            )
                                        )}
                                    </div>
                                </section>

                                {/* Detected Defects */}
                                <section className="mb-8">
                                    <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                                        Detected Defects (
                                        {submission.defects.length})
                                    </h3>
                                    {submission.defects.length > 0 ? (
                                        <div className="space-y-3">
                                            {submission.defects.map(
                                                (defect: Defect) => (
                                                    <div
                                                        key={defect.id}
                                                        className="bg-slate-50 dark:bg-zinc-800 rounded-lg p-4 border border-slate-200 dark:border-zinc-700"
                                                    >
                                                        <div className="flex items-start justify-between mb-2">
                                                            <div className="flex items-center gap-2">
                                                                <span className="font-mono text-sm font-semibold text-slate-900 dark:text-white">
                                                                    {defect.id}
                                                                </span>
                                                                <span
                                                                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${getSeverityBadgeColor(
                                                                        defect.severity
                                                                    )}`}
                                                                >
                                                                    {getSeverityIcon(
                                                                        defect.severity
                                                                    )}
                                                                    {defect.severity.toUpperCase()}
                                                                </span>
                                                            </div>
                                                            <span className="text-xs text-slate-500 dark:text-zinc-500">
                                                                @ (
                                                                {defect.location.x}
                                                                %,{" "}
                                                                {defect.location.y}
                                                                %)
                                                            </span>
                                                        </div>
                                                        <p className="text-slate-700 dark:text-zinc-300">
                                                            {defect.description}
                                                        </p>
                                                    </div>
                                                )
                                            )}
                                        </div>
                                    ) : (
                                        <div className="bg-green-50 dark:bg-green-500/10 rounded-lg p-4 border border-green-200 dark:border-green-500/20 text-center">
                                            <p className="text-green-700 dark:text-green-400">
                                                No defects detected
                                            </p>
                                        </div>
                                    )}
                                </section>

                                {/* Detailed Analysis */}
                                <section>
                                    <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                                        Detailed Analysis
                                    </h3>
                                    <div className="bg-slate-50 dark:bg-zinc-800 rounded-lg p-6 border border-slate-200 dark:border-zinc-700">
                                        <pre className="whitespace-pre-wrap font-mono text-sm text-slate-700 dark:text-zinc-300 leading-relaxed">
                                            {submission.analysis}
                                        </pre>
                                    </div>
                                </section>
                            </div>
                        ))}
                    </div>

                    {/* Report Footer */}
                    <div className="bg-slate-100 dark:bg-zinc-800 px-8 py-4 border-t border-slate-200 dark:border-zinc-700">
                        <p className="text-sm text-slate-600 dark:text-zinc-400 text-center">
                            Generated by GLaDOS AI Anomaly Detection System •{" "}
                            {today}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
