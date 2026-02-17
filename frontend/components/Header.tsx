"use client";

/**
 * Header component for the application.
 */

import { Activity, FolderOpen, Sun, Moon, LogOut } from "lucide-react";
import { useApp } from "@/lib/app-context";

export default function Header({
    onSwitchProject,
    onLogout,
}: {
    onSwitchProject?: () => void;
    onLogout?: () => void;
}) {
    const { theme, currentProject, toggleTheme } = useApp();

    return (
        <header className="fixed top-0 left-0 right-0 z-50 bg-white dark:bg-zinc-900 border-b border-slate-200 dark:border-zinc-800">
            <div className="max-w-[1800px] mx-auto px-6 py-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-blue-600 dark:bg-blue-500 rounded flex items-center justify-center">
                                <Activity
                                    className="w-5 h-5 text-white"
                                    strokeWidth={2.5}
                                />
                            </div>
                            <h1 className="text-xl font-bold text-slate-900 dark:text-white">
                                GLaDOS
                            </h1>
                        </div>

                        {/* Current Project Display */}
                        {currentProject && (
                            <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 dark:bg-zinc-800 rounded-lg border border-slate-200 dark:border-zinc-700">
                                <FolderOpen className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                                <span className="text-sm font-medium text-slate-900 dark:text-white">
                                    {currentProject.name}
                                </span>
                                {onSwitchProject && (
                                    <button
                                        onClick={onSwitchProject}
                                        className="text-xs text-slate-500 dark:text-zinc-500 hover:text-blue-600 dark:hover:text-blue-400 ml-2 transition-colors"
                                    >
                                        Switch
                                    </button>
                                )}
                            </div>
                        )}
                    </div>
                    <div className="flex items-center gap-3">
                        <button
                            onClick={toggleTheme}
                            className="p-2 rounded-lg bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-400 hover:bg-slate-200 dark:hover:bg-zinc-700 transition-colors"
                            title={
                                theme === "dark"
                                    ? "Switch to Light Mode"
                                    : "Switch to Dark Mode"
                            }
                        >
                            {theme === "dark" ? (
                                <Sun className="w-5 h-5" />
                            ) : (
                                <Moon className="w-5 h-5" />
                            )}
                        </button>
                        {onLogout && (
                            <button
                                onClick={onLogout}
                                className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors"
                                title="Logout"
                            >
                                <LogOut className="w-5 h-5 text-slate-600 dark:text-zinc-400" />
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </header>
    );
}