import type { Metadata } from "next";
import "./globals.css";
import ClientRoot from "./ClientRoot";

export const metadata: Metadata = {
    title: "GLaDOS",
    description: "General Local Anomoly Detection Observation System",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" suppressHydrationWarning className="overscroll-none">
            <body className="antialiased">
                <ClientRoot>{children}</ClientRoot>
            </body>
        </html>
    );
}
