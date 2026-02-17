"use client";

/**
 * Page for creating new projects and viewing all projects.
 */

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
    Activity,
    FileText,
    Plus,
    X,
    ArrowRight,
    FolderOpen,
} from "lucide-react";
import Header from "@/components/Header";
import { useApp } from "@/lib/app-context";
import { cn } from "@/lib/utils";

// TODO: Replace with API call to fetch projects
// This is dummy data for development
const DUMMY_PROJECTS = [
    {
        id: "proj-1",
        name: "Circuit Board QA - Model XR-500",
        createdAt: new Date("2024-01-15"),
        updatedAt: new Date("2024-01-20"),
        designSpecs: ["spec-1.pdf", "spec-2.pdf"],
    },
    {
        id: "proj-2",
        name: "Mobile Device Testing - Series 7",
        createdAt: new Date("2024-02-01"),
        updatedAt: new Date("2024-02-10"),
        designSpecs: ["mobile-spec.pdf"],
    },
    {
        id: "proj-3",
        name: "Automotive Component Inspection",
        createdAt: new Date("2024-02-15"),
        updatedAt: new Date("2024-02-18"),
        designSpecs: ["auto-spec-1.pdf", "auto-spec-2.pdf", "auto-spec-3.pdf"],
    },
];

export default function ProjectsPage() {
    const router = useRouter();
    const { setCurrentProject } = useApp();
    const [projectName, setProjectName] = useState("");
    const [designSpecs, setDesignSpecs] = useState<File[]>([]);
    const [showNewProject, setShowNewProject] = useState(
        DUMMY_PROJECTS.length === 0
    );

    // TODO: Replace with API call to fetch projects
    const existingProjects = DUMMY_PROJECTS;

    // Clear current project when on projects page
    useEffect(() => {
        setCurrentProject(null);
    }, [setCurrentProject]);

    const handleDesignSpecUpload = (
        e: React.ChangeEvent<HTMLInputElement>
    ) => {
        if (e.target.files) {
            const newFiles = Array.from(e.target.files);
            setDesignSpecs((prev) => {
                const existingNames = new Set(prev.map((f) => f.name));
                const uniqueNewFiles = newFiles.filter(
                    (file) => !existingNames.has(file.name)
                );
                return [...prev, ...uniqueNewFiles];
            });
            // Reset the input so the same file can be selected again if needed
            e.target.value = "";
        }
    };

    const removeDesignSpec = (index: number) => {
        setDesignSpecs((prev) => prev.filter((_, i) => i !== index));
    };

    const handleCreateProject = () => {
        if (projectName.trim() && designSpecs.length > 0) {
            const newProject = {
                id: `proj-${Date.now()}`,
                name: projectName.trim(),
                createdAt: new Date(),
                updatedAt: new Date(),
                designSpecs: designSpecs.map((file) => file.name),
            };

            // TODO: Replace with API call to create project
            // For now, just set it in context and navigate
            setCurrentProject(newProject);
            router.push("/inspect");
        }
    };

    const handleSelectProject = (project: typeof DUMMY_PROJECTS[0]) => {
        setCurrentProject(project);
        router.push("/inspect");
    };

    return (
        <div className="h-screen bg-slate-50 dark:bg-zinc-950 transition-colors flex flex-col overflow-hidden">
            <Header />
            {!showNewProject && existingProjects.length > 0 ? (
                <div className="flex-1 flex flex-col pt-24 overflow-hidden">
                    <div className="max-w-[1200px] w-full mx-auto px-6 pt-6 pb-2 flex-shrink-0">
                        <div className="text-center mb-8">
                            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-3">
                                Project Setup
                            </h1>
                            <p className="text-slate-600 dark:text-zinc-400">
                                Select an existing project or create a new one
                            </p>
                        </div>
                        <div className="max-w-[800px] mx-auto">
                            {/* Header with Your Projects and Create Button */}
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                                    Your Projects
                                </h2>
                                <button
                                    onClick={() => setShowNewProject(true)}
                                    className="flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-300 dark:border-zinc-700 hover:border-blue-400 dark:hover:border-blue-600 bg-white dark:bg-zinc-900 hover:bg-slate-50 dark:hover:bg-zinc-800 transition-all"
                                >
                                    <Plus className="w-4 h-4 text-slate-600 dark:text-zinc-400" />
                                    <span className="text-sm text-slate-900 dark:text-white font-medium">
                                        Create New Project
                                    </span>
                                </button>
                            </div>
                        </div>
                    </div>
                    {/* Scrollable Projects List */}
                    <div className="flex-1 overflow-y-auto">
                        <div className="max-w-[1200px] w-full mx-auto px-6 pb-8">
                            <div className="max-w-[800px] mx-auto">
                                <div className="space-y-3">
                                    {existingProjects.map((project) => (
                                        <button
                                            key={project.id}
                                            onClick={() => handleSelectProject(project)}
                                            className="w-full text-left p-5 rounded-xl border-2 border-slate-200 dark:border-zinc-800 hover:border-blue-400 dark:hover:border-blue-600 hover:bg-white dark:hover:bg-zinc-900 bg-white dark:bg-zinc-900/50 transition-all group"
                                        >
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-3 mb-2">
                                                        <FolderOpen className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                                                        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                                                            {project.name}
                                                        </h3>
                                                    </div>
                                                    <p className="text-sm text-slate-500 dark:text-zinc-500 mb-2">
                                                        {project.designSpecs?.length || 0}{" "}
                                                        design specification
                                                        {(project.designSpecs?.length || 0) !== 1
                                                            ? "s"
                                                            : ""}
                                                    </p>
                                                    <p className="text-xs text-slate-400 dark:text-zinc-600">
                                                        Created{" "}
                                                        {project.createdAt.toLocaleDateString(
                                                            "en-US",
                                                            {
                                                                month: "short",
                                                                day: "numeric",
                                                                year: "numeric",
                                                            }
                                                        )}
                                                    </p>
                                                </div>
                                                <ArrowRight className="w-5 h-5 text-slate-400 dark:text-zinc-600 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" />
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                <main className="flex-1 overflow-y-auto pt-24">
                    <div className="max-w-[1200px] mx-auto px-6 py-6">
                        <div className="text-center mb-8">
                            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-3">
                                Project Setup
                            </h1>
                            <p className="text-slate-600 dark:text-zinc-400">
                                Create a new project with design specifications
                            </p>
                        </div>
                        <div className="max-w-[700px] mx-auto">
                            {/* New Project Form */}
                            <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl p-8">
                                {/* Project Name */}
                                <div className="mb-8">
                                    <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-3">
                                        Project Name
                                    </label>
                                    <input
                                        type="text"
                                        value={projectName}
                                        onChange={(e) => setProjectName(e.target.value)}
                                        placeholder="e.g., Circuit Board QA - Model XR-500"
                                        className="w-full px-4 py-3 bg-white dark:bg-zinc-950 border border-slate-300 dark:border-zinc-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-600 transition-colors"
                                    />
                                </div>

                                {/* Design Specifications */}
                                <div>
                                    <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-3">
                                        Design Specification(s)
                                    </label>

                                    <div className="border-2 border-dashed border-slate-300 dark:border-zinc-700 rounded-xl p-8 text-center bg-slate-50 dark:bg-zinc-950 hover:border-blue-400 dark:hover:border-blue-600 transition-colors mb-4">
                                        <input
                                            type="file"
                                            id="design-spec"
                                            onChange={handleDesignSpecUpload}
                                            accept=".pdf,.txt"
                                            multiple
                                            className="hidden"
                                        />
                                        <label
                                            htmlFor="design-spec"
                                            className="cursor-pointer block"
                                        >
                                            <FileText className="w-10 h-10 text-slate-400 dark:text-zinc-600 mx-auto mb-3" />
                                            <p className="text-slate-900 dark:text-white mb-1">
                                                Drop files here or{" "}
                                                <span className="text-blue-600 dark:text-blue-400 font-medium">
                                                    browse
                                                </span>
                                            </p>
                                            <p className="text-sm text-slate-500 dark:text-zinc-500">
                                                PDF or TXT files
                                            </p>
                                        </label>
                                    </div>

                                    {/* Uploaded Specs List */}
                                    {designSpecs.length > 0 && (
                                        <div className="space-y-4 mb-4">
                                            {designSpecs.map((file, index) => (
                                                <div
                                                    key={index}
                                                    className="flex items-center justify-between bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 rounded-lg p-3 hover:border-slate-300 dark:hover:border-zinc-700 transition-colors"
                                                >
                                                    <div className="flex items-center gap-3 min-w-0 flex-1">
                                                        <div className="w-9 h-9 bg-blue-50 dark:bg-blue-500/10 rounded flex items-center justify-center flex-shrink-0">
                                                            <FileText className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                                                        </div>
                                                        <span className="text-sm text-slate-900 dark:text-white truncate font-medium">
                                                            {file.name}
                                                        </span>
                                                    </div>
                                                    <button
                                                        onClick={() => removeDesignSpec(index)}
                                                        className="text-slate-400 dark:text-zinc-600 hover:text-red-500 dark:hover:text-red-400 transition-colors ml-2 p-1"
                                                        title="Remove file"
                                                    >
                                                        <X className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>

                                {/* Create Project Button */}
                                <button
                                    onClick={handleCreateProject}
                                    disabled={!projectName.trim() || designSpecs.length === 0}
                                    className={cn(
                                        "w-full font-semibold py-4 px-6 rounded-xl transition-all disabled:cursor-not-allowed shadow-sm mt-6",
                                        projectName.trim() && designSpecs.length > 0
                                            ? "bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 hover:dark:bg-blue-600 text-white"
                                            : "bg-slate-300 dark:bg-zinc-800 text-slate-500 dark:text-zinc-600"
                                    )}
                                >
                                    Create Project
                                </button>

                                {/* Back to Projects List */}
                                {existingProjects.length > 0 && (
                                    <button
                                        onClick={() => setShowNewProject(false)}
                                        className="w-full text-sm text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white mt-4 py-2 transition-colors"
                                    >
                                        ← Back to projects
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                </main>
            )}
        </div>
    );
}
