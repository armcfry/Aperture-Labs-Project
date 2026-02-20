"use client";

import { AppLayout } from "@/components/layout";
import AppProvider from "./AppProvider";

/**
 * Client wrapper that mounts the context, providers, and app layout
 */

export default function ClientRoot({ children }: { children: React.ReactNode }) {
    return (
        <AppProvider>
            <AppLayout>{children}</AppLayout>
        </AppProvider>
    );
}
